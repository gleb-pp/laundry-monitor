import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils.components import render_page_header, render_quote
from config import settings

st.set_page_config(page_title="Laundry Monitor", page_icon="🧺", layout="wide")
st_autorefresh(interval=30000, key="main_auto")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] { display: none; }
        .stDeployButton { display: none; }
        .main > div { padding: 2rem 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# Header with title and refresh button
render_page_header("Laundry Monitor", "🧺", show_back=False)

# Display inspirational quote
render_quote()

st.markdown("### Choose Machine Type")
st.markdown("Select a category below to view availability or report a machine.")

col1, col2 = st.columns(2)


with col1, st.container(border=True):
    st.image(str(settings.WASHER_IMAGE), width=150)
    st.subheader("Washing Machines")
    st.write("Check washer availability and submit status updates.")
    if st.button(
        "Browse Washers",
        key="goto_washers",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/washers.py")

with col2, st.container(border=True):
    st.image(str(settings.DRYER_IMAGE), width=138)
    st.subheader("Dryers")
    st.write("Check dryer availability and submit status updates.")
    if st.button(
        "Browse Dryers",
        key="goto_dryers",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/dryers.py")
