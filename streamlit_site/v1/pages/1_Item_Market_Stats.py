import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

import altair as alt
import polars as pl
import streamlit as st
from pages.mappings.map_item_data import item_info_column_config, item_categories
from utils.bdolytics_hook.bdolytics import (
    BDOlyticsAnalyticsEndpoint,
    _convert_from_epoch,
)
from utils.bdolytics_hook.configs.config import LOCALES
from utils.peak_hours import define_peak_hours, filter_for_times
from utils.pearl_abyss_hook.pa_base_item_info import ItemData
from utils.pearl_abyss_hook.pa_market_read import MarketData
from statistics import mean, stdev
from millify import millify

st.set_page_config(layout="wide")
with st.expander("🕰️ A note on Timezones."):
    st.markdown(
        """
                Due to the way Altair and Vega (the charting provider here) handle timezone information,
                you will notice that, no matter the region you select in the sidebar, the chart will always
                display your localized timezone as the x-axis. This is known behavior and is not a bug.

                While the Red "Peak Hour" bands are correct, the x axis is localized _to your timezone_.
                """
    )


# Convert data to a DataFrame
def prepare_data(
    item_id: int, regions: list = None
) -> list[BDOlyticsAnalyticsEndpoint]:
    endpoint = BDOlyticsAnalyticsEndpoint()
    return endpoint.fill__analytics_request(item_id=item_id, regions=regions)


def create_chart(
    region: str = None,
    models: list[BDOlyticsAnalyticsEndpoint] = None,
    localized_tz: str = "UTC",
) -> alt.Chart:
    data_pd = pl.DataFrame._from_records(
        [model.model_dump() for model in models]
    ).to_pandas()
    data_pd["epoch_timestamp"] = (
        data_pd["epoch_timestamp"]
        .apply(lambda x: _convert_from_epoch(x))
        .dt.tz_convert(localized_tz)
    )
    # remove the item_id column
    data_pd = data_pd.drop(columns=["item_id"])
    data_pd = data_pd.melt("epoch_timestamp")

    # Make a rectangle for peak hours

    peak_hours = define_peak_hours(regions=region)
    peak_hours_df = filter_for_times(models, peak_hours).to_pandas()
    peak_hours_df["min_epoch"] = peak_hours_df["min_epoch"].dt.tz_localize(localized_tz)
    peak_hours_df["max_epoch"] = peak_hours_df["max_epoch"].dt.tz_localize(localized_tz)

    areas = (
        alt.Chart(peak_hours_df.reset_index())
        .mark_rect(
            opacity=0.3,
        )
        .encode(
            x=alt.X("min_epoch:T", title="Peak Hours", axis=alt.Axis(format="%H:%M")),
            x2="max_epoch:T",
            y=alt.value(0),
            y2=alt.value(200),
            color=alt.value("red"),
        )
    )
    lines = (
        alt.Chart()
        .mark_line(
            interpolate="step-after",
        )
        .encode(
            x="epoch_timestamp:T",
            y="value:Q",
            color="variable:N",
        )
        .properties(height=200, width=1000)
    )

    nearest = alt.selection_point(
        nearest=True,
        on="mouseover",
        fields=["epoch_timestamp"],
        empty="none",
    )

    selectors = (
        alt.Chart()
        .mark_point()
        .encode(
            x="epoch_timestamp:T",
            opacity=alt.value(0),
            tooltip=[
                alt.Tooltip("epoch_timestamp:T", format="%Y-%m-%d %H:%M:%S%Z"),
                "value:Q",
            ],
        )
        .add_selection(nearest)
    )

    points = lines.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = lines.mark_text(align="left", dx=5, dy=-5, color="white").encode(
        text=alt.condition(nearest, "value:Q", alt.value(" "))
    )

    rules = (
        alt.Chart()
        .mark_rule(color="white")
        .encode(
            x="epoch_timestamp:T",
        )
        .transform_filter(nearest)
    )

    return (
        alt.layer(lines, selectors, points, text, rules, areas)
        .facet(row="variable:N", data=data_pd)
        .properties(title="Price and Volume Over Time")
        .resolve_scale(y="independent", x="shared")
        .configure_headerRow(
            titleColor="white",
            labelColor="white",
            labelPadding=-10,
            titlePadding=-8,
            titleFontSize=16,
            labelFontSize=14,
        )
        .configure_axis(
            titleOpacity=0,
            titlePadding=5,
        )
    )


@st.cache_data
def get_pa_market_item_data(item_id: int, item_category_id: int = None) -> pl.DataFrame:
    return (
        ItemData(item_category_id)
        .get_base_item_data()
        .filter(pl.col("mainKey") == item_id)
    )


@st.cache_resource
def get_pa_market_items(item_category_id: int) -> pl.DataFrame:
    return ItemData(item_category_id).get_base_item_data()


@st.cache_data
def get_pa_trade_data(
    item_id: int, region: str = "na", endpoint_name: str = "GET_WORLD_MARKET_SUB_LIST"
) -> list[MarketData]:
    return MarketData(
        item_id=item_id, region=region, endpoint_name=endpoint_name
    ).parse_response()


def make_pa_trade_item_human(
    cat_key: str,
) -> list[str]:
    data = get_pa_market_items(item_categories[cat_key]["category_id"])
    main_keys = data["mainKey"].to_list()
    names = data["name"].to_list()

    return [f"{mk} - {name}" for mk, name in zip(main_keys, names)]


def calculate_stdev_score(ints: list[int]) -> float:
    return (mean(ints), round(stdev(ints), 2))


def calculate_volatility_sentiment(mean: float, stdev: float) -> str:
    thresholds = [
        (0.10, "-Non-Volatile"),
        (0.25, "-Slightly Volatile"),
        (0.33, "+Volatile"),
        (0.50, "+Very Volatile"),
        (0.75, "+Extremely Volatile"),
    ]

    for factor, label in thresholds:
        if mean * factor > stdev:
            return label

    return "+Unstable"


def calculate_volume_vs_stock_sentiment(volume: list[int], stock: list[int]) -> tuple[str, str]:
    """
    Calculate the relationship between trading volume and stock availability.
    
    Parameters:
        volume (list[int]): List of trading volumes for an item.
        stock (list[int]): List of stock availability for an item.
    
    Returns:
        Tuple[str, str]: A tuple containing a short description and a longer explanation.
    """
    # Precompute sums for efficiency
    total_volume = sum(volume)
    total_stock = sum(stock)

    # Determine sentiment based on volume and stock
    if total_volume == 0:
        if total_stock == 0:
            return ("Slowly Traded Item", "+Item rarely appears on the market.")
        else:
            return ("Stock > Volume", "-Item is being listed more than traded. There may be a surplus at times.")
    else:
        if total_stock == 0:
            return ("Likely High Value Item", "+There is not enough stock to ever meet demand. Item sold as soon as it is listed.")
        elif total_volume >= total_stock:
            return ("Volume > Stock", "+Item is being traded more than listed. There may be a shortage at times.")
        else:
            return ("Stock > Volume", "-Item is being listed more than traded. There may be a surplus at times.")


def color_grade(val: int) -> str:
    color_map = {0: None, 1: "green", 2: "blue", 3: "yellow", 4: "orange"}
    color = color_map.get(val, None)
    return f"background-color: {color}"


# Sidebar
st.sidebar.header("Sidebar")
item_cats = st.sidebar.selectbox(
    "Select a Category:", ["Choose Category. . .", *list(item_categories)]
)
if item_cats != "Choose Category. . .":
    item_id = st.sidebar.selectbox(
        "Select an Item:",
        ["Begin typing to search. . .", *make_pa_trade_item_human(item_cats)],
    )
regions: str = st.sidebar.selectbox("Select Region:", [loc.upper() for loc in LOCALES])
generate_button = st.sidebar.button("Generate Chart")
reset_cache_button = st.sidebar.button("Reset Cache")

if reset_cache_button:
    st.cache_data.clear()
    st.cache_resource.clear()


timezones = {
    "NA": "America/New_York",
    "EU": "Europe/London",
    "SA": "America/Sao_Paulo",
    "SEA": "Asia/Singapore",
    "TW": "Asia/Taipei",
    "KR": "Asia/Seoul",
    "RU": "Europe/Moscow",
    "JP": "Asia/Tokyo",
    "MENA": "Asia/Dubai",
}

if generate_button:
    st.header(f"Market Stats for {item_id.split(' - ')[1]}")
    data_models = prepare_data(int(item_id.split(" - ")[0].strip()), regions=[regions])

    col1, col2, col3, col4 = st.columns(4)
    colr1, colr2 = st.columns(2)
    # Item Info
    with st.spinner("Loading Item Data..."):
        base_item_info = get_pa_market_item_data(
            int(item_id.split(" - ")[0].strip()),
            item_categories[item_cats]["category_id"],
        ).to_pandas()
        base_trade_info = get_pa_trade_data(
            int(item_id.split(" - ")[0].strip()), region=regions
        )
    st.dataframe(
        base_item_info.style.applymap(color_grade, subset=["grade"]),
        hide_index=True,
        use_container_width=True,
        column_config=item_info_column_config,
    )
    ##
    # Market Stats
    price_variance = calculate_stdev_score(
        [model.model_dump()["price"] for model in data_models]
    )
    base_vol_stock = calculate_volume_vs_stock_sentiment(
        [model.model_dump()["volume"] for model in data_models],
        [model.model_dump()["stock"] for model in data_models],
    )

    col1.metric(
        "Current Price w/ 1 Day Rolling Change",
        millify(data_models[0].model_dump()["price"], 3),
        millify(
            data_models[0].model_dump()["price"] - data_models[8].model_dump()["price"],
            3,
        ),
        help="1 Day Rolling Delta",
    )
    col2.metric(
        "Current Stock w/ 1 Day Rolling Change",
        millify(data_models[0].model_dump()["stock"], 3),
        millify(
            data_models[0].model_dump()["stock"] - data_models[8].model_dump()["stock"],
            3,
        ),
        help="1 Day Rolling Delta",
    )
    col3.metric(
        "Current Volume w/ 1 Day Rolling Change",
        millify(data_models[0].model_dump()["volume"], 2),
        millify(
            data_models[0].model_dump()["volume"]
            - data_models[8].model_dump()["volume"],
            2,
        ),
        help="1 Day Rolling Delta",
    )
    col4.metric(
        "Price Volatility Score",
        f"±{price_variance[1]}",
        calculate_volatility_sentiment(price_variance[0], price_variance[1]),
        delta_color="inverse",
        help=(
            "Standard Deviation of Price over the time period. "
            "A lower value indicates the price is generally more stable over the time period."
        ),
    )

    colr1.metric(
        "Volume vs Stock Daily",
        base_vol_stock[0],
        base_vol_stock[1],
        help=(
            "Volume is the amount of items traded. Stock is the amount of items available to purchase. "
            "Note that this is historical data."
        ),
    )

    colr2.metric(
        "Last Sale Price",
        millify(base_trade_info[0].model_dump()["last_sale_price"], 3),
        millify(base_trade_info[0].model_dump()["last_sale_price"] - data_models[0].model_dump()["price"], 3),
        help="The most recently recorded sale price for this item. Direct from Pearl Abyss.",
    )

    st.altair_chart(
        create_chart(
            region=regions, models=data_models, localized_tz=timezones[regions]
        ),
        use_container_width=True,
    )
