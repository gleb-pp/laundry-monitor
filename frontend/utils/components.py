import streamlit as st

from utils.api_client import (
    get_random_quote,
    submit_report,
    get_machine_history,
)
from utils.helpers import format_status, get_status_color


def render_page_header(
    title: str,
    icon: str = "",
    show_back: bool = False,
) -> None:
    """Render the top navigation with Title and a top-right Refresh button."""
    col_back, col_title, col_refresh = st.columns([1, 7, 2])

    with col_back:
        if show_back and st.button("⬅️ Back", use_container_width=True):
            st.switch_page("app.py")

    with col_title:
        st.title(f"{icon} {title}")

    with col_refresh:
        if st.button(
            "Refresh",
            use_container_width=True,
            key=f"refresh_{title}",
        ):
            st.cache_data.clear()
            st.rerun()

    st.divider()


def render_quote() -> None:
    """Display the cached random quote."""
    quote = get_random_quote()
    st.info(f"💡 {quote}")


def render_machine_card(machine: dict, icon_url: str) -> None:
    """Render a UI card for a single laundry machine."""
    with st.container(border=True):
        col_img, col_info = st.columns([1, 3])

        with col_img:
            st.image(icon_url, width=100)

        with col_info:
            st.subheader(machine.get("name", "Unnamed"))
            st.caption(
                f"Dorm: {machine.get('dormitory', '?')}| ID: {machine.get('id', '?')}",
            )

        status = machine.get("status", "unavailable")
        color = get_status_color(status)
        status_text = format_status(status)

        st.markdown(
            f"""
            <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                <span style='display:inline-block; width:12px; height:12px;
                            background-color:{color}; border-radius:50%;
                            margin-right: 8px;'></span>
                <strong>Status:</strong>&nbsp;{status_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if (
            status != "free" and
            st.button(
                "✅ Quick: Mark Free",
                key=f"quick_free_{machine['id']}",
                use_container_width=True,
            ) and
            submit_report(machine_id=machine["id"], status="free")
        ):
            st.success("Status updated!")
            st.rerun()

        with st.popover("📝 Detailed Report", use_container_width=True):
            st.write("Submit new status report")
            rep_status = st.radio(
                "Machine Status",
                options=["busy", "free", "unavailable"],
                key=f"radio_{machine['id']}",
                horizontal=True,
            )
            time_rem = None
            if rep_status == "busy":
                time_rem = st.number_input(
                    "Time remaining (minutes)",
                    min_value=0, value=30, step=5,
                    key=f"time_{machine['id']}",
                )
            reporter_name = st.text_input(
                "Your Name (Optional)",
                key=f"reporter_{machine['id']}",
            )

            if st.button(
                "Submit Report",
                key=f"submit_{machine['id']}",
                type="primary",
                use_container_width=True,
            ):
                success = submit_report(
                    machine_id=machine["id"],
                    status=rep_status,
                    time_remaining=time_rem,
                    reporter=reporter_name,
                )
                if success:
                    st.success("Report submitted successfully!")
                    st.rerun()


def render_admin_machine_card(machine: dict, icon_url: str) -> None:
    """Render a UI card for a laundry machine in the Admin Panel with history."""

    with st.container(border=True):
        col_img, col_info = st.columns([1, 3])

        with col_img:
            st.image(icon_url, width=100)

        with col_info:
            st.subheader(machine.get("name", "Unnamed"))
            st.caption(f"Dorm: {machine.get('dormitory', '?')} | Type: {machine.get('type', '?').title()}")

        status = machine.get("status", "unavailable")
        color = get_status_color(status)
        status_text = format_status(status)

        st.markdown(
            f"<div style='display: flex; align-items: center; margin-bottom: 15px;'>"
            f"<span style='display:inline-block; width:12px; height:12px; background-color:{color}; border-radius:50%; margin-right: 8px;'></span>"
            f"<strong>Status:</strong>&nbsp;{status_text}</div>",
            unsafe_allow_html=True
        )

        with st.popover("📜 View History", use_container_width=True):
            st.write(f"**Recent reports for {machine.get('name')}**")

            history = get_machine_history(machine["id"])

            if not history:
                st.info("No history found for this machine.")
            else:
                formatted_history = []
                for rep in history:
                    raw_time = rep.get("timestamp", "")
                    clean_time = raw_time.replace("T", " ")[:19] if raw_time else "Unknown"

                    time_rem = rep.get("time_remaining")

                    formatted_history.append({
                        "Status": format_status(rep.get("status", "")),
                        "Time": clean_time,
                        "Rem. (min)": time_rem if time_rem is not None else "-"
                    })

                st.dataframe(
                    formatted_history,
                    hide_index=True,
                    use_container_width=True,
                )
