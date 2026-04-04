import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.api_client import get_machines, submit_report, get_random_quote
from utils.helpers import get_status_color, format_status

st.set_page_config(page_title="Dryers", page_icon="🧺", layout="wide")

st_autorefresh(interval=20000, key="dryers_auto")

st.markdown(
    """
    <style>
        /* Скрыть боковую панель навигации */
        section[data-testid="stSidebar"] {
            display: none;
        }
        /* Скрыть кнопку Deploy */
        .stDeployButton {
            display: none;
        }
        /* Убрать отступ для основного контента (чтобы не было пустоты слева) */
        .main > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* Сделать кнопку Refresh маленькой */
        div.stButton > button:has(span:contains("Refresh")) {
            font-size: 0.8rem;
            padding: 0.2rem 0.6rem;
            background-color: #f0f2f6;
            border: 1px solid #ccc;
            border-radius: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧺 Dryers")
quote = get_random_quote()
st.markdown(f"> {quote}")

machines = get_machines()
dryers = [m for m in machines if m.get("type") == "drying"]

if not dryers:
    st.info("No dryers found.")
else:
    cols = st.columns(3)
    for idx, machine in enumerate(dryers):
        with cols[idx % 3]:
            with st.container(border=True):
                st.image("https://cdn-icons-png.flaticon.com/512/3032/3032064.png", width=80)
                st.subheader(machine.get("name", "Unnamed"))
                dorm = machine.get("dormitory", "?")
                id = machine.get("id", "?")
                st.write(f"Dormitory: {dorm}")
                st.write(f"ID: {id}")
                
                status = machine.get("status", "unavailable")
                color = get_status_color(status)
                status_text = format_status(status)
                st.markdown(
                    f"<span style='display:inline-block; width:12px; height:12px; background-color:{color}; border-radius:50%;'></span> "
                    f"<strong>Status:</strong> {status_text}",
                    unsafe_allow_html=True
                )
                
                with st.popover("📝 Report this machine"):
                    st.write(f"Report for **{machine['name']}**")
                    rep_status = st.selectbox(
                        "Status",
                        options=["busy", "free", "unavailable"],
                        key=f"status_{machine['id']}"
                    )
                    time_rem = None
                    if rep_status == "busy":
                        time_rem = st.number_input(
                            "Time remaining (minutes)", 
                            min_value=0, value=30, step=5,
                            key=f"time_{machine['id']}"
                        )
                    if st.button("Submit report", key=f"submit_{machine['id']}"):
                        success = submit_report(
                            machine_id=machine['id'],
                            status=rep_status,
                            time_remaining=time_rem
                        )
                        if success:
                            st.success("Report submitted! Refreshing...")
                            st.rerun()


col_back, col_refresh = st.columns([1, 1])
with col_back:
    if st.button("Return back", key="back_home"):
        st.switch_page("app.py")
with col_refresh:
    if st.button("Refresh", key="refresh_washers"):
        st.cache_data.clear()
        st.rerun()