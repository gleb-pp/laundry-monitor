import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("LAUNDRY_API_URL", "http://localhost:8000")
TIMEOUT = 5

@st.cache_data(ttl=30, show_spinner=False)
def get_machines():
    """Fetches the list of all machines from the backend API."""
    try:
        resp = requests.get(f"{API_BASE_URL}/machines", timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Failed to fetch machines: {e}")
        return []

@st.cache_data(ttl=30, show_spinner=False)
def get_random_quote():
    """Fetches a random inspirational quote (Cached for 1 hour to prevent UI lag)."""
    try:
        url = "http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en"
        response = requests.get(url, timeout=3)
        data = response.json()
        quote_text = data['quoteText']
        quote_author = data['quoteAuthor']
        if (quote_author):
            return f"“{quote_text}” — {quote_author}"
        return f"“{quote_text}”"
    except Exception:
        return "“The secret of getting ahead is getting started.” — Mark Twain"

def submit_report(machine_id: int, status: str, time_remaining: int = None, reporter: str = None):
    """Submits a new status report to the backend API."""
    params = {"machine_id": machine_id, "status": status}
    if time_remaining is not None:
        params["time_remaining"] = time_remaining
    if reporter:
        params["reporter_name"] = reporter

    try:
        resp = requests.post(f"{API_BASE_URL}/report", params=params, timeout=TIMEOUT)
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