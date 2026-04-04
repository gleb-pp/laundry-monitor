import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.api_client import get_random_quote

st.set_page_config(page_title="Laundry Monitor", page_icon="🧺", layout="wide")

# Автообновление каждые 20 секунд
st_autorefresh(interval=20000, key="main_auto")

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

st.title("🧺 Laundry Monitor")

# Цитата
quote = get_random_quote()
st.markdown(f"> {quote}")

st.markdown("## Choose machine type")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.image("https://cdn-icons-png.flaticon.com/512/2920/2920245.png", width=120)  # стиралка
        st.subheader("Washing Machine")
        st.write("View all washing machines and report status")
        if st.button("Go to Washers", key="goto_washers", use_container_width=True):
            st.switch_page("pages/washers.py")

with col2:
    with st.container(border=True):
        st.image("https://cdn-icons-png.flaticon.com/512/3032/3032064.png", width=120)  # сушилка
        st.subheader("Dryer")
        st.write("View all dryers and report status")
        if st.button("Go to Dryers", key="goto_dryers", use_container_width=True):
            st.switch_page("pages/dryers.py")

col_left, col_right = st.columns([6, 1])
with col_right:
    if st.button("Refresh", key="refresh_main"):
        st.cache_data.clear()
        st.rerun()