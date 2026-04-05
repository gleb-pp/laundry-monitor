import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.api_client import get_machines
from utils.components import render_machine_card, render_page_header, render_quote
from config import settings

st.set_page_config(page_title="Washing Machines", page_icon="🌊", layout="wide")
st_autorefresh(interval=30000, key="washers_auto")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] { display: none; }
        .stDeployButton { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

render_page_header("Washing Machines", "🌊", show_back=True)
render_quote()

machines = get_machines()
washers = [m for m in machines if m.get("type") == "washing"]

if not washers:
    st.info("No washing machines currently available in the database.")
else:
    cols = st.columns(3)
    for idx, machine in enumerate(washers):
        with cols[idx % 3]:
            render_machine_card(
                machine=machine,
                icon_url=str(settings.WASHER_CARD_IMAGE),
            )
