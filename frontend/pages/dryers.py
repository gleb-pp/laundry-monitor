import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils.api_client import get_machines
from utils.components import (
    render_machine_card,
    render_page_header,
    render_quote,
)
from config import settings

st.set_page_config(page_title="Dryers", page_icon="💨", layout="wide")
st_autorefresh(interval=30000, key="dryers_auto")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] { display: none; }
        .stDeployButton { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

render_page_header("Dryers", "💨", show_back=True)
render_quote()

machines = get_machines()
dryers = [m for m in machines if m.get("type") == "drying"]

if not dryers:
    st.info("No dryers currently available in the database.")
else:
    cols = st.columns(3)
    for idx, machine in enumerate(dryers):
        with cols[idx % 3]:
            render_machine_card(
                machine=machine,
                icon_url=str(settings.DRYER_CARD_IMAGE),
            )
