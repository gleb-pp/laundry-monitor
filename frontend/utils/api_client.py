from typing import Any

import requests
import streamlit as st

from config import settings


@st.cache_data(ttl=30, show_spinner=False)
def get_machines() -> list[dict[str, Any]] | None:
    """Fetch the list of all machines from the backend API."""
    try:
        resp = requests.get(
            f"{settings.API_BASE_URL}/machines",
            timeout=settings.TIMEOUT,
            )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Failed to fetch machines: {e}")
        return None


@st.cache_data(ttl=30, show_spinner=False)
def get_random_quote() -> str:
    """Fetch a random inspirational quote (Cached for 30 sec to prevent UI lag)."""
    try:
        url = "http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en"
        response = requests.get(url, timeout=3)
        data = response.json()
        quote_text = data["quoteText"]
        quote_author = data["quoteAuthor"]
        if (quote_author):
            return f"“{quote_text}” — {quote_author}"
        return f"“{quote_text}”"
    except Exception:
        return "“The secret of getting ahead is getting started.” — Mark Twain"


def submit_report(
    machine_id: int,
    status: str,
    time_remaining: int | None = None,
    reporter: str | None = None,
) -> bool:
    """Submit a new status report to the backend API."""
    params = {"machine_id": machine_id, "status": status}
    if time_remaining is not None:
        params["time_remaining"] = time_remaining
    if reporter:
        params["reporter_name"] = reporter

    try:
        resp = requests.post(
            f"{settings.API_BASE_URL}/report",
            params=params,
            timeout=settings.TIMEOUT,
        )
        resp.raise_for_status()
        st.cache_data.clear()
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            st.error(f"Validation error (422): {e.response.text}")
        else:
            st.error(f"Report submission failed: {e}")
        return False
    except Exception as e:
        st.error(f"Report submission failed: {e}")
        return False


@st.cache_data(ttl=10, show_spinner=False)
def get_machine_history(
    machine_id: int,
    limit: int = 10,
) -> list[dict[str, Any]] | None:
    """Fetch the history of a specific machine."""
    try:
        resp = requests.get(
            f"{settings.API_BASE_URL}/machines/{machine_id}/history",
            params={"limit": limit},
            timeout=settings.TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Failed to fetch history for machine {machine_id}: {e}")
        return None
