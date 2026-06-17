from unittest.mock import patch


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "model" in body
    assert "auth_required" in body


def test_profile_crud(client, sample_profile_payload):
    r = client.post("/api/profiles", json=sample_profile_payload)
    assert r.status_code == 200, r.text
    pid = r.json()["id"]

    r = client.get(f"/api/profiles/{pid}")
    assert r.json()["full_name"] == "Jane Doe"

    updated = {**sample_profile_payload, "full_name": "Jane D."}
    r = client.put(f"/api/profiles/{pid}", json=updated)
    assert r.json()["full_name"] == "Jane D."

    r = client.get("/api/profiles")
    assert any(p["id"] == pid for p in r.json())

    r = client.delete(f"/api/profiles/{pid}")
    assert r.status_code == 200


@patch("app.routers.jds.parse_jd")
def test_jd_create_with_mocked_claude(parse_mock, client, fake_parsed_jd):
    parse_mock.return_value = fake_parsed_jd
    r = client.post("/api/jds", json={"raw_text": "Some posting", "source": "private"})
    assert r.status_code == 200, r.text
    assert r.json()["company"] == "FooCorp"
    assert r.json()["role"] == "Backend Engineer"


def test_jd_create_rejects_empty(client):
    r = client.post("/api/jds", json={"raw_text": "   "})
    assert r.status_code == 400


@patch("app.routers.jds.parse_jd")
def test_application_crud_and_dashboard(parse_mock, client, sample_profile_payload, fake_parsed_jd):
    parse_mock.return_value = fake_parsed_jd
    profile_id = client.post("/api/profiles", json=sample_profile_payload).json()["id"]
    jd_id = client.post("/api/jds", json={"raw_text": "raw", "source": "private"}).json()["id"]

    r = client.post(
        "/api/applications",
        json={"profile_id": profile_id, "jd_id": jd_id, "template_type": "private"},
    )
    assert r.status_code == 200, r.text
    app_id = r.json()["id"]

    r = client.patch(f"/api/applications/{app_id}", json={"status": "applied"})
    assert r.json()["status"] == "applied"

    r = client.get("/api/applications/dashboard/summary")
    body = r.json()
    assert body["total"] == 1
    assert body["by_status"].get("applied") == 1
    assert len(body["recent"]) == 1
    assert body["recent"][0]["company"] == "FooCorp"
