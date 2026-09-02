"""Tests de los endpoints de Categorias."""

BASE = "/api/v1/categories"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_category(client):
    response = client.post(BASE, json={"name": "Comida"})
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Comida"
    assert created["description"] is None
    assert isinstance(created["id"], int)

    response = client.get(f"{BASE}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_duplicate_name_returns_409(client):
    client.post(BASE, json={"name": "Transporte"})
    response = client.post(BASE, json={"name": "Transporte"})
    assert response.status_code == 409


def test_get_missing_category_returns_404(client):
    assert client.get(f"{BASE}/999").status_code == 404


def test_update_category(client):
    category_id = client.post(BASE, json={"name": "Ocio"}).json()["id"]

    response = client.patch(f"{BASE}/{category_id}", json={"description": "Cine, juegos"})
    assert response.status_code == 200
    assert response.json()["description"] == "Cine, juegos"
    assert response.json()["name"] == "Ocio"


def test_delete_category(client):
    category_id = client.post(BASE, json={"name": "Salud"}).json()["id"]

    assert client.delete(f"{BASE}/{category_id}").status_code == 204
    assert client.get(f"{BASE}/{category_id}").status_code == 404


def test_list_categories(client):
    client.post(BASE, json={"name": "A"})
    client.post(BASE, json={"name": "B"})

    response = client.get(BASE)
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["A", "B"]


def test_name_is_required(client):
    assert client.post(BASE, json={}).status_code == 422
