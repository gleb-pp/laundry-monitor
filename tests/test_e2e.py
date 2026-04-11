from datetime import UTC, datetime, timedelta, timezone
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


def test_e2e_seeded_machines_are_available_on_startup(
    client: TestClient,
) -> None:
    """App starts, seeds machines, and returns them via the API."""
    response = client.get("/machines")

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 4
    assert {machine["name"] for machine in body} == {
        "Washer 1",
        "Dryer 1",
        "Washer 2",
        "Dryer 2",
    }
    assert all("status" in machine for machine in body)


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
    machines_before = client.get("/machines")
    assert machines_before.status_code == 200

    target_machine = next(
        machine for machine in machines_before.json()
        if machine["id"] == 1
    )
    assert target_machine["status"] == "free"

    post_response = client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "busy",
            "time_remaining": 25,
        },
    )
    assert post_response.status_code == 200
    assert post_response.json() == {"success": True}

    machines_after = client.get("/machines")
    assert machines_after.status_code == 200
    updated_machine = next(
        machine for machine in machines_after.json()
        if machine["id"] == 1
    )
    assert updated_machine["status"] == "busy"

    history_response = client.get("/machines/1/history")
    assert history_response.status_code == 200
    history = history_response.json()

    assert len(history) >= 1
    assert history[0]["machine_id"] == 1
    assert history[0]["status"] == "busy"
    assert history[0]["time_remaining"] == 25


@patch("src.service.machine.datetime", FixedDateTime)
@patch("src.models.reports.datetime", FixedDateTime)
def test_e2e_expired_busy_report_becomes_free(
    client: TestClient,
) -> None:
    """
    Full flow with time logic:
    a BUSY report with expired remaining time should make the machine FREE.
    """
    FixedDateTime.current = datetime(2026, 4, 11, 12, 0, tzinfo=UTC)

    response = client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "busy",
            "time_remaining": 30,
        },
    )
    assert response.status_code == 200

    FixedDateTime.current = datetime(2026, 4, 11, 12, 40, tzinfo=UTC)

    machines_response = client.get("/machines")
    assert machines_response.status_code == 200
    machine = next(
        item for item in machines_response.json()
        if item["id"] == 1
    )
    assert machine["status"] == "free"


@patch("src.service.machine.datetime", FixedDateTime)
@patch("src.models.reports.datetime", FixedDateTime)
def test_e2e_busy_without_remaining_becomes_probably_free_after_threshold(
    client: TestClient,
) -> None:
    FixedDateTime.current = datetime(2026, 4, 11, 8, 0, tzinfo=UTC)

    post_response = client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "busy",
        },
    )
    assert post_response.status_code == 200

    FixedDateTime.current = datetime(2026, 4, 11, 13, 0, tzinfo=UTC)

    machines_response = client.get("/machines")
    assert machines_response.status_code == 200
    machine = next(item for item in machines_response.json() if item["id"] == 1)
    assert machine["status"] == "probably_free"


@patch("src.service.machine.datetime", FixedDateTime)
@patch("src.models.reports.datetime", FixedDateTime)
def test_e2e_busy_with_remaining_becomes_free_after_expiry(
    client: TestClient,
) -> None:
    FixedDateTime.current = datetime(2026, 4, 11, 12, 0, tzinfo=UTC)

    post_response = client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "busy",
            "time_remaining": 30,
        },
    )
    assert post_response.status_code == 200

    FixedDateTime.current = datetime(2026, 4, 11, 12, 31, tzinfo=UTC)

    machines_response = client.get("/machines")
    assert machines_response.status_code == 200
    machine = next(item for item in machines_response.json() if item["id"] == 1)
    assert machine["status"] == "free"


def test_e2e_latest_report_wins_in_status_calculation(
    client: TestClient,
) -> None:
    """
    If several reports exist, the latest one must define the visible status.
    """
    response_1 = client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "unavailable",
        },
    )
    assert response_1.status_code == 200

    response_2 = client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "free",
        },
    )
    assert response_2.status_code == 200

    machines_response = client.get("/machines")
    assert machines_response.status_code == 200
    machine = next(
        item for item in machines_response.json()
        if item["id"] == 1
    )
    assert machine["status"] == "free"

    history_response = client.get("/machines/1/history")
    assert history_response.status_code == 200
    history = history_response.json()

    assert len(history) >= 2
    assert history[0]["status"] == "free"
    assert history[1]["status"] == "unavailable"
