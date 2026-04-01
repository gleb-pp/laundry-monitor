def test_get_machines_returns_seeded_machines(client):
    response = client.get("/machines")

    assert response.status_code == 200
    body = response.json()

    assert isinstance(body, list)
    assert len(body) == 4

    first = body[0]
    assert {"id", "dormitory", "name", "type", "status"} <= set(first.keys())


def test_post_report_returns_success(client):
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


def test_history_contains_posted_report(client):
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


def test_machines_endpoint_reflects_unavailable_status(client):
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


def test_history_limit_parameter_works(client):
    client.post("/report", params={"machine_id": 1, "status": "free"})
    client.post("/report", params={"machine_id": 1, "status": "busy", "time_remaining": 10})

    response = client.get("/machines/1/history", params={"limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1