from fastapi.testclient import TestClient


def test_get_machines_returns_seeded_machines(client: TestClient) -> None:
    """Check that the GET /machines endpoint returns the seeded machines."""
    response = client.get("/machines")

    assert response.status_code == 200
    body = response.json()

    assert isinstance(body, list)
    assert len(body) == 4

    first = body[0]
    assert {"id", "dormitory", "name", "type", "status"} <= set(first.keys())


def test_post_report_returns_success(client: TestClient) -> None:
    """Check that the POST /report endpoint returns success."""
    response = client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "busy",
            "time_remaining": 25,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_history_contains_posted_report(client: TestClient) -> None:
    """
    Check that a report posted to POST /report appears in the
    GET /machines/{machine_id}/history endpoint.
    """
    client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "busy",
            "time_remaining": 25,
        },
    )

    response = client.get("/machines/1/history")

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 1
    assert body[0]["machine_id"] == 1
    assert body[0]["status"] == "busy"
    assert body[0]["time_remaining"] == 25


def test_machines_endpoint_reflects_unavailable_status(
    client: TestClient,
) -> None:
    """Check that the machines endpoint reflects the unavailable status."""
    client.post(
        "/report",
        params={
            "machine_id": 1,
            "status": "unavailable",
        },
    )

    response = client.get("/machines")
    assert response.status_code == 200

    machine = next(item for item in response.json() if item["id"] == 1)
    assert machine["status"] == "unavailable"


def test_history_limit_parameter_works(client: TestClient) -> None:
    """
    Check that the limit parameter of GET /machines/{machine_id}/history
    limits the number of returned reports.
    """
    client.post("/report", params={"machine_id": 1, "status": "free"})
    client.post(
        "/report",
        params={"machine_id": 1, "status": "busy", "time_remaining": 10},
    )

    response = client.get("/machines/1/history", params={"limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1


def test_history_limit_parameter_returns_latest_report(
    client: TestClient,
) -> None:
    """
    Check that the limit parameter of GET /machines/{machine_id}/history
    returns the latest report.
    """
    client.post("/report", params={"machine_id": 1, "status": "free"})
    client.post(
        "/report",
        params={"machine_id": 1, "status": "busy", "time_remaining": 10},
    )

    response = client.get("/machines/1/history", params={"limit": 1})

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 1
    assert body[0]["machine_id"] == 1
    assert body[0]["status"] == "busy"
    assert body[0]["time_remaining"] == 10
