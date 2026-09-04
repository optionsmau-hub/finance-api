"""Tests de los endpoints de Presupuestos."""

BUD = "/api/v1/budgets"
CAT = "/api/v1/categories"


def _payload(category_id: int, **overrides) -> dict:
    data = {"category_id": category_id, "month": "2026-09", "limit_amount": "500"}
    data.update(overrides)
    return data


def test_create_budget(client, category_id):
    response = client.post(BUD, json=_payload(category_id))
    assert response.status_code == 201
    body = response.json()
    assert body["month"] == "2026-09"
    assert body["category_id"] == category_id


def test_invalid_month_format_is_rejected(client, category_id):
    assert client.post(BUD, json=_payload(category_id, month="2026-9")).status_code == 422


def test_create_with_unknown_category_returns_404(client):
    assert client.post(BUD, json=_payload(9999)).status_code == 404


def test_duplicate_budget_returns_409(client, category_id):
    client.post(BUD, json=_payload(category_id))
    response = client.post(BUD, json=_payload(category_id))
    assert response.status_code == 409


def test_list_budgets_filtered_by_month(client, category_id):
    other_category = client.post(CAT, json={"name": "Transporte"}).json()["id"]
    client.post(BUD, json=_payload(category_id))
    client.post(BUD, json=_payload(other_category, month="2026-10", limit_amount="200"))

    result = client.get(BUD, params={"month": "2026-09"}).json()
    assert len(result) == 1
    assert result[0]["month"] == "2026-09"


def test_update_budget_amount(client, category_id):
    budget_id = client.post(BUD, json=_payload(category_id)).json()["id"]

    response = client.patch(f"{BUD}/{budget_id}", json={"limit_amount": "750"})
    assert response.status_code == 200
    assert float(response.json()["limit_amount"]) == 750


def test_delete_budget(client, category_id):
    budget_id = client.post(BUD, json=_payload(category_id)).json()["id"]

    assert client.delete(f"{BUD}/{budget_id}").status_code == 204
    assert client.get(f"{BUD}/{budget_id}").status_code == 404


def test_deleting_category_cascades_to_its_budget(client, category_id):
    budget_id = client.post(BUD, json=_payload(category_id)).json()["id"]

    # La categoria no tiene transacciones, asi que se puede borrar; al
    # borrarla, su presupuesto se va con ella (ON DELETE CASCADE).
    assert client.delete(f"{CAT}/{category_id}").status_code == 204
    assert client.get(f"{BUD}/{budget_id}").status_code == 404
