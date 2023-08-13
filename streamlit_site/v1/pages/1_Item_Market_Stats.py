import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

import altair as alt
import polars as pl
import streamlit as st
from utils.bdolytics_hook.bdolytics import BDOlyticsAnalyticsEndpoint
from utils.bdolytics_hook.configs.config import LOCALES
from utils.peak_hours import define_peak_hours, filter_for_times

st.set_page_config(layout="wide")

# Convert data to a DataFrame
def prepare_data(item_id: int, regions: list = None) -> list[BDOlyticsAnalyticsEndpoint]:
    endpoint = BDOlyticsAnalyticsEndpoint()
    return endpoint.fill__analytics_request(item_id=item_id, regions=regions)


def create_chart(region: str = None, models: list[BDOlyticsAnalyticsEndpoint] = None) -> alt.Chart:
    data_pd = pl.DataFrame._from_records([model.model_dump() for model in models]).to_pandas()
    # remove the item_id column
    data_pd = data_pd.drop(columns=["item_id"])
    data_pd = data_pd.melt("epoch_timestamp")

    # Make a rectangle for peak hours

    peak_hours = define_peak_hours(regions=region)
    peak_hours_df = filter_for_times(models, peak_hours).to_pandas()

    areas = (alt.Chart(peak_hours_df)
             .mark_rect(
                 opacity=0.3,
             )
             .encode(
                 x="min_epoch:T",
                 x2="max_epoch:T",
                 y=alt.value(0),
                 y2=alt.value(300),
                color=alt.value("red"),
             ))
    lines = (
            alt.Chart()
            .mark_line()
            .encode(
                x="epoch_timestamp:T",
                y="value:Q",
                color="variable:N",
            )
            .properties(height=200, width=1000)
        )

    nearest = alt.selection(
        type="single",
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
                alt.Tooltip("epoch_timestamp:T", format="%Y-%m-%d %H:%M:%S"),
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
        alt.layer(areas, lines, selectors, points, text, rules)
        .facet(row="variable:N", data=data_pd)
        .properties(title="Price and Volume Over Time")
        .resolve_scale(y="independent")
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

if generate_button:
    st.sidebar.write("Generating chart for Item ID:", item_id)

    data_models = prepare_data(item_id, regions=[regions])
    st.altair_chart(create_chart(region=regions, models=data_models), use_container_width=True)