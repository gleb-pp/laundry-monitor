import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("LAUNDRY_API_URL", "http://localhost:8000")

@st.cache_data(ttl=30, show_spinner=False)
def get_machines():
    try:
        resp = requests.get(f"{API_BASE_URL}/machines")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Failed to fetch machines: {e}")
        return []

def get_random_quote():
    try:
        url = "http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en"
        response = requests.get(url)
        data = response.json()
        quote_text = data['quoteText']
        quote_author = data['quoteAuthor']
        return f"“{quote_text}” — {quote_author}"
    except Exception:
        return "“The secret of getting ahead is getting started.” — Mark Twain"

def submit_report(machine_id: int, status: str, time_remaining: int = None):
    # Отправляем статус в нижнем регистре (значение Enum)
    params = {"machine_id": machine_id, "status": status}
    if time_remaining is not None:
        params["time_remaining"] = time_remaining

    try:
        resp = requests.post(f"{API_BASE_URL}/report", params=params)
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