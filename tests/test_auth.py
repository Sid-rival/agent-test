def test_register_and_login(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "u@example.com", "password": "secret123", "full_name": "U"},
    )
    assert r.status_code == 201
    assert r.json()["email"] == "u@example.com"

    r = client.post(
        "/api/v1/auth/login",
        data={"username": "u@example.com", "password": "secret123"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()

    # duplicate registration -> 409
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "u@example.com", "password": "secret123"},
    )
    assert r.status_code == 409


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": "secret123"})
    r = client.post("/api/v1/auth/login", data={"username": "a@example.com", "password": "wrong"})
    assert r.status_code == 401
