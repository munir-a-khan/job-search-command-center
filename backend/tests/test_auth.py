def test_auth_disabled_when_api_key_empty(client):
    # default fixture has API_KEY=""
    r = client.get("/api/profiles")
    assert r.status_code == 200


def test_auth_required_rejects_missing_key(client_with_auth):
    client, _ = client_with_auth
    r = client.get("/api/profiles")
    assert r.status_code == 401


def test_auth_required_accepts_correct_key(client_with_auth):
    client, key = client_with_auth
    r = client.get("/api/profiles", headers={"X-API-Key": key})
    assert r.status_code == 200


def test_auth_rejects_wrong_key(client_with_auth):
    client, _ = client_with_auth
    r = client.get("/api/profiles", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_health_does_not_require_auth(client_with_auth):
    client, _ = client_with_auth
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["auth_required"] is True
