"""Tests de registro, login y aislamiento de datos entre usuarios."""

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
CAT = "/api/v1/categories"

EMAIL = "ana@example.com"
PASSWORD = "supersecret"


def test_register_creates_user(raw_client):
    response = raw_client.post(REGISTER, json={"email": EMAIL, "password": PASSWORD})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == EMAIL
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_returns_409(raw_client):
    raw_client.post(REGISTER, json={"email": EMAIL, "password": PASSWORD})
    response = raw_client.post(REGISTER, json={"email": EMAIL, "password": "otraclave"})
    assert response.status_code == 409


def test_register_rejects_short_password(raw_client):
    response = raw_client.post(REGISTER, json={"email": EMAIL, "password": "123"})
    assert response.status_code == 422


def test_login_returns_token(raw_client):
    raw_client.post(REGISTER, json={"email": EMAIL, "password": PASSWORD})
    response = raw_client.post(LOGIN, data={"username": EMAIL, "password": PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_login_with_wrong_password_returns_401(raw_client):
    raw_client.post(REGISTER, json={"email": EMAIL, "password": PASSWORD})
    response = raw_client.post(LOGIN, data={"username": EMAIL, "password": "incorrecta"})
    assert response.status_code == 401


def test_login_with_unknown_email_returns_401(raw_client):
    response = raw_client.post(LOGIN, data={"username": "nadie@example.com", "password": "x"})
    assert response.status_code == 401


def test_categories_endpoint_requires_token(raw_client):
    assert raw_client.get(CAT).status_code == 401
    assert raw_client.post(CAT, json={"name": "Comida"}).status_code == 401


def test_invalid_token_is_rejected(raw_client):
    raw_client.headers["Authorization"] = "Bearer esto-no-es-un-token-valido"
    assert raw_client.get(CAT).status_code == 401


def test_authenticated_client_can_use_the_api(client):
    response = client.post(CAT, json={"name": "Comida"})
    assert response.status_code == 201


def test_user_cannot_see_another_users_category(client, other_client):
    created = client.post(CAT, json={"name": "Comida"}).json()

    # El otro usuario no la ve en su listado...
    assert other_client.get(CAT).json() == []
    # ...ni puede acceder a ella por id (404, no 403: no revelamos que existe).
    assert other_client.get(f"{CAT}/{created['id']}").status_code == 404


def test_two_users_can_have_a_category_with_the_same_name(client, other_client):
    r1 = client.post(CAT, json={"name": "Comida"})
    r2 = other_client.post(CAT, json={"name": "Comida"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["id"] != r2.json()["id"]
