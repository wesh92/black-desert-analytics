import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

import altair as alt
import polars as pl
import streamlit as st
from utils.bdolytics_hook.bdolytics import BDOlyticsAnalyticsEndpoint
from utils.bdolytics_hook.configs.config import LOCALES
from utils.peak_hours import define_peak_hours, filter_for_times
from utils.bdolytics_hook.bdolytics import _convert_from_epoch

st.set_page_config(layout="wide")
st.markdown(
    """
            🕰️ A note on Timezones.

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


st.title("Market Stats")

# Sidebar
st.sidebar.header("Sidebar")
item_id = st.sidebar.number_input("Enter Item ID:", value=575)
regions = st.sidebar.selectbox("Select Region:", [loc.upper() for loc in LOCALES])
generate_button = st.sidebar.button("Generate Chart")

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
    st.sidebar.write("Generating chart for Item ID:", item_id)

    col1, col2, col3 = st.columns(3)

    data_models = prepare_data(item_id, regions=[regions])

    col1.metric(
        "Current Price 1 Day Rolling Change",
        data_models[0].model_dump()["price"],
        data_models[0].model_dump()["price"] - data_models[8].model_dump()["price"],
        help="1 Day Rolling Delta",
    )
    col2.metric(
        "Current Stock 1 Day Rolling Change",
        data_models[0].model_dump()["stock"],
        data_models[0].model_dump()["stock"] - data_models[8].model_dump()["stock"],
        help="1 Day Rolling Delta",
    )
    col3.metric(
        "Current Volume 1 Day Rolling Change",
        data_models[0].model_dump()["volume"],
        data_models[0].model_dump()["volume"] - data_models[8].model_dump()["volume"],
        help="1 Day Rolling Delta",
    )

    st.altair_chart(
        create_chart(
            region=regions, models=data_models, localized_tz=timezones[regions]
        ),
        use_container_width=True,
    )
