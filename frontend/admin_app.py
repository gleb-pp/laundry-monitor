import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils.api_client import get_machines
from utils.components import (
    render_page_header,
    render_admin_machine_card,
)
from config import settings

st.set_page_config(
    page_title="Admin Panel - Laundry",
    page_icon="⚙️",
    layout="wide",
)
st_autorefresh(interval=30000, key="admin_auto")

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

render_page_header("Admin Panel - All Machines", "⚙️", show_back=False)

machines = get_machines()

if not machines:
    st.info("No machines currently available in the database.")
else:
    cols = st.columns(3)
    for idx, machine in enumerate(machines):
        with cols[idx % 3]:
            if machine.get("type") == "washing":
                icon_url = str(settings.WASHER_CARD_IMAGE)
            else:
                icon_url = str(settings.DRYER_CARD_IMAGE)

            render_admin_machine_card(machine=machine, icon_url=icon_url)
