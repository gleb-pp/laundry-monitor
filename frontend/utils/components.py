import streamlit as st
from utils.api_client import submit_report, get_random_quote
from utils.helpers import get_status_color, format_status


def render_page_header(title: str, icon: str = "", show_back: bool = False):
    """Renders the top navigation with Title and a top-right Refresh button."""
    # Используем 3 колонки: для кнопки назад, для заголовка, для кнопки обновления
    col_back, col_title, col_refresh = st.columns([1, 7, 2])

    with col_back:
        if show_back:
            if st.button("⬅️ Back", use_container_width=True):
                st.switch_page("app.py")

    with col_title:
        st.title(f"{icon} {title}")

    with col_refresh:
        # Кнопка Refresh всегда справа сверху
        if st.button("Refresh", use_container_width=True, key=f"refresh_{title}"):
            st.cache_data.clear()
            st.rerun()

    st.divider()


def render_quote():
    """Displays the cached random quote."""
    quote = get_random_quote()
    st.info(f"💡 {quote}")


def render_machine_card(machine: dict, icon_url: str):
    """Renders a UI card for a single laundry machine."""
    with st.container(border=True):
        col_img, col_info = st.columns([1, 3])

        with col_img:
            st.image(icon_url, width=100)

        with col_info:
            st.subheader(machine.get("name", "Unnamed"))
            st.caption(f"Dorm: {machine.get('dormitory', '?')} | ID: {machine.get('id', '?')}")

        status = machine.get("status", "unavailable")
        color = get_status_color(status)
        status_text = format_status(status)

        st.markdown(
            f"<div style='display: flex; align-items: center; margin-bottom: 15px;'>"
            f"<span style='display:inline-block; width:12px; height:12px; background-color:{color}; border-radius:50%; margin-right: 8px;'></span>"
            f"<strong>Status:</strong>&nbsp;{status_text}</div>",
            unsafe_allow_html=True
        )

        if status != "free":
            if st.button("✅ Quick: Mark Free", key=f"quick_free_{machine['id']}", use_container_width=True):
                if submit_report(machine_id=machine['id'], status="free"):
                    st.success("Status updated!")
                    st.rerun()

        with st.popover("📝 Detailed Report", use_container_width=True):
            st.write("Submit new status report")
            rep_status = st.radio(
                "Machine Status",
                options=["busy", "free", "unavailable"],
                key=f"radio_{machine['id']}",
                horizontal=True
            )
            time_rem = None
            if rep_status == "busy":
                time_rem = st.number_input(
                    "Time remaining (minutes)",
                    min_value=0, value=30, step=5,
                    key=f"time_{machine['id']}"
                )
            reporter_name = st.text_input("Your Name (Optional)", key=f"reporter_{machine['id']}")

            if st.button("Submit Report", key=f"submit_{machine['id']}", type="primary", use_container_width=True):
                success = submit_report(
                    machine_id=machine['id'],
                    status=rep_status,
                    time_remaining=time_rem,
                    reporter=reporter_name
                )
                if success:
                    st.success("Report submitted successfully!")
                    st.rerun()
