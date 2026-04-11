from datetime import UTC, datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient


class FixedDateTime:
    """Mock datetime with mutable current time."""
    current = datetime(2026, 4, 11, 12, 0, tzinfo=UTC)

    @classmethod
    def now(cls, tz: timezone | None = None) -> datetime:
        if tz is not None:
            return cls.current.astimezone(tz)
        return cls.current


def _get_machines(client: TestClient) -> list[dict]:
    response = client.get("/machines")
    response.raise_for_status()
    return response.json()


def _get_machine(client: TestClient, machine_id: int) -> dict:
    return next(machine for machine in _get_machines(client) if machine["id"] == machine_id)


def _get_history(client: TestClient, machine_id: int) -> list[dict]:
    response = client.get(f"/machines/{machine_id}/history")
    response.raise_for_status()
    return response.json()


def _post_report(
    client: TestClient,
    machine_id: int,
    status: str,
    time_remaining: int | None = None,
) -> dict:
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
    """App starts, seeds machines, and returns them via the API."""
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
    """
    Full user flow:
    1. user sees machines,
    2. sends a BUSY report,
    3. sees updated machine status,
    4. sees the same report in history.
    """
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
    FixedDateTime.current = datetime(2026, 4, 11, 8, 0, tzinfo=UTC)
    _post_report(client, 1, "busy")

    FixedDateTime.current = datetime(2026, 4, 11, 13, 0, tzinfo=UTC)
    assert _get_machine(client, 1)["status"] == "probably_free"


@patch("src.service.machine.datetime", FixedDateTime)
@patch("src.models.reports.datetime", FixedDateTime)
def test_e2e_busy_with_remaining_becomes_free_after_expiry(
    client: TestClient,
) -> None:
    FixedDateTime.current = datetime(2026, 4, 11, 12, 0, tzinfo=UTC)
    _post_report(client, 1, "busy", 30)

    FixedDateTime.current = datetime(2026, 4, 11, 12, 31, tzinfo=UTC)
    assert _get_machine(client, 1)["status"] == "free"


def test_e2e_latest_report_wins_in_status_calculation(
    client: TestClient,
) -> None:
    """
    If several reports exist, the latest one must define the visible status.
    """
    _post_report(client, 1, "unavailable")
    _post_report(client, 1, "free")

    assert _get_machine(client, 1)["status"] == "free"
    assert [report["status"] for report in _get_history(client, 1)[:2]] == [
        "free",
        "unavailable",
    ]
