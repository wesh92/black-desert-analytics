import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="👋",
)

st.write("# Welcome to Black Desert Deep Analytics! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    This is a constant work-in-progress. Please be patient as we continue to
    develop this site. The major goal of the work here is to provide perscriptive actions
    for players to take in order to maximize their in-game profits.

    **👈 Select a demo from the sidebar** to see some examples.
    ### Major Thanks to:
    - Warflash and [BDOlytics.](https://bdolytics.com/en/NA)
        - Many of the ideas and data used here are from BDOlytics. In addition, Warflash has generously provided access to their API.
    - [Summer on youtube an many other places.](https://www.youtube.com/@summer_rains)
        - For the incredibly helpful videos he makes for the community and for the inspiration to make this site.
"""  # noqa: E501
)
