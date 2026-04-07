def get_status_color(status: str) -> str:
    """Return CSS color for a given status."""
    colors = {
        "free": "#2ecc71",           # green
        "busy": "#e74c3c",           # red
        "probably_free": "#f1c40f",  # yellow
        "unavailable": "#95a5a6",    # grey
    }
    return colors.get(status, "#95a5a6")


def format_status(status: str) -> str:
    """Return human-readable status."""
    return status.replace("_", " ").title()
