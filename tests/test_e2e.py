from datetime import UTC, datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient


class FixedDateTime:
    """Mock datetime class with a mutable current timestamp for time-based tests."""

    current = datetime(2026, 4, 11, 12, 0, tzinfo=UTC)

    @classmethod
    def now(cls, tz: timezone | None = None) -> datetime:
        """Return the mocked current time, optionally converted to the given timezone."""
        if tz is not None:
            return cls.current.astimezone(tz)
        return cls.current


def _get_machines(client: TestClient) -> list[dict]:
    """Fetch all machines from the API and return the parsed JSON response."""
    response = client.get("/machines")
    response.raise_for_status()
    return response.json()


def _get_machine(client: TestClient, machine_id: int) -> dict:
    """Fetch all machines and return the one matching the given machine ID."""
    return next(
        machine for machine in _get_machines(client)
        if machine["id"] == machine_id
    )


def _get_history(client: TestClient, machine_id: int) -> list[dict]:
    """Fetch the report history for a specific machine and return it as JSON."""
    response = client.get(f"/machines/{machine_id}/history")
    response.raise_for_status()
    return response.json()


def _post_report(
    client: TestClient,
    machine_id: int,
    status: str,
    time_remaining: int | None = None,
) -> dict:
    """Send a machine status report to the API and return the parsed JSON response."""
    params = {
        "machine_id": machine_id,
        "status": status,
    }
    if time_remaining is not None:
        params["time_remaining"] = time_remaining

    response = client.post("/report", params=params)
    response.raise_for_status()
    return response.json()


def test_e2e_seeded_machines_are_available_on_startup(
    client: TestClient,
) -> None:
    """Verify that the application starts with the seeded machines available and free."""
    machines = _get_machines(client)

    assert {
        (machine["name"], machine["status"])
        for machine in machines
    } == {
        ("Washer 1", "free"),
        ("Dryer 1", "free"),
        ("Washer 2", "free"),
        ("Dryer 2", "free"),
    }


def test_e2e_report_changes_machine_status_and_history(
    client: TestClient,
) -> None:
    """Verify that posting a BUSY report updates both machine status and history."""
    assert _get_machine(client, 1)["status"] == "free"
    assert _post_report(client, 1, "busy", 25) == {"success": True}
    assert _get_machine(client, 1)["status"] == "busy"

    latest_report = _get_history(client, 1)[0]
    assert {
        "machine_id": 1,
        "status": "busy",
        "time_remaining": 25,
    }.items() <= latest_report.items()


@patch("src.service.machine.datetime", FixedDateTime)
@patch("src.models.reports.datetime", FixedDateTime)
def test_e2e_busy_without_remaining_becomes_probably_free_after_threshold(
    client: TestClient,
) -> None:
    """Verify that a BUSY report without remaining time becomes probably_free after the threshold."""
    FixedDateTime.current = datetime(2026, 4, 11, 8, 0, tzinfo=UTC)
    _post_report(client, 1, "busy")

    FixedDateTime.current = datetime(2026, 4, 11, 13, 0, tzinfo=UTC)
    assert _get_machine(client, 1)["status"] == "probably_free"


@patch("src.service.machine.datetime", FixedDateTime)
@patch("src.models.reports.datetime", FixedDateTime)
def test_e2e_busy_with_remaining_becomes_free_after_expiry(
    client: TestClient,
) -> None:
    """Verify that a BUSY report with remaining time becomes free after the deadline expires."""
    FixedDateTime.current = datetime(2026, 4, 11, 12, 0, tzinfo=UTC)
    _post_report(client, 1, "busy", 30)

    FixedDateTime.current = datetime(2026, 4, 11, 12, 31, tzinfo=UTC)
    assert _get_machine(client, 1)["status"] == "free"


def test_e2e_latest_report_wins_in_status_calculation(
    client: TestClient,
) -> None:
    """Verify that the latest report determines the visible machine status and history order."""
    _post_report(client, 1, "unavailable")
    _post_report(client, 1, "free")

    assert _get_machine(client, 1)["status"] == "free"
    assert [report["status"] for report in _get_history(client, 1)[:2]] == [
        "free",
        "unavailable",
    ]
