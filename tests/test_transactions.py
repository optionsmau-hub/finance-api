"""Tests de los endpoints de Transacciones."""

from decimal import Decimal

TX = "/api/v1/transactions"
CAT = "/api/v1/categories"


def _payload(category_id: int, **overrides) -> dict:
    data = {
        "amount": "50.00",
        "type": "expense",
        "occurred_on": "2026-01-15",
        "note": "Almuerzo",
        "category_id": category_id,
    }
    data.update(overrides)
    return data


def test_create_transaction(client, category_id):
    response = client.post(TX, json=_payload(category_id))
    assert response.status_code == 201
    body = response.json()
    assert Decimal(str(body["amount"])) == Decimal("50.00")
    assert body["type"] == "expense"
    assert body["category_id"] == category_id
    assert isinstance(body["id"], int)
    assert "created_at" in body


def test_amount_must_be_positive(client, category_id):
    assert client.post(TX, json=_payload(category_id, amount="0")).status_code == 422
    assert client.post(TX, json=_payload(category_id, amount="-10")).status_code == 422


def test_invalid_type_is_rejected(client, category_id):
    assert client.post(TX, json=_payload(category_id, type="transfer")).status_code == 422


def test_create_with_unknown_category_returns_404(client):
    assert client.post(TX, json=_payload(9999)).status_code == 404


def test_get_transaction(client, category_id):
    created = client.post(TX, json=_payload(category_id)).json()
    response = client.get(f"{TX}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_transaction_returns_404(client):
    assert client.get(f"{TX}/999").status_code == 404


def test_list_is_ordered_most_recent_first(client, category_id):
    client.post(TX, json=_payload(category_id, occurred_on="2026-01-01", note="vieja"))
    client.post(TX, json=_payload(category_id, occurred_on="2026-03-01", note="nueva"))

    notes = [t["note"] for t in client.get(TX).json()]
    assert notes == ["nueva", "vieja"]


def test_filter_by_type(client, category_id):
    client.post(TX, json=_payload(category_id, type="income", amount="1000"))
    client.post(TX, json=_payload(category_id, type="expense", amount="30"))

    result = client.get(TX, params={"type": "income"}).json()
    assert len(result) == 1
    assert result[0]["type"] == "income"


def test_filter_by_category(client, category_id):
    other = client.post(CAT, json={"name": "Transporte"}).json()["id"]
    client.post(TX, json=_payload(category_id))
    client.post(TX, json=_payload(other))

    result = client.get(TX, params={"category_id": other}).json()
    assert [t["category_id"] for t in result] == [other]


def test_filter_by_date_range(client, category_id):
    client.post(TX, json=_payload(category_id, occurred_on="2026-01-10"))
    client.post(TX, json=_payload(category_id, occurred_on="2026-02-10"))
    client.post(TX, json=_payload(category_id, occurred_on="2026-03-10"))

    result = client.get(TX, params={"date_from": "2026-02-01", "date_to": "2026-02-28"}).json()
    assert [t["occurred_on"] for t in result] == ["2026-02-10"]


def test_update_transaction(client, category_id):
    tx_id = client.post(TX, json=_payload(category_id)).json()["id"]

    response = client.patch(f"{TX}/{tx_id}", json={"amount": "75.50", "note": "corregido"})
    assert response.status_code == 200
    assert Decimal(str(response.json()["amount"])) == Decimal("75.50")
    assert response.json()["note"] == "corregido"


def test_update_with_unknown_category_returns_404(client, category_id):
    tx_id = client.post(TX, json=_payload(category_id)).json()["id"]
    assert client.patch(f"{TX}/{tx_id}", json={"category_id": 9999}).status_code == 404


def test_delete_transaction(client, category_id):
    tx_id = client.post(TX, json=_payload(category_id)).json()["id"]
    assert client.delete(f"{TX}/{tx_id}").status_code == 204
    assert client.get(f"{TX}/{tx_id}").status_code == 404


def test_cannot_delete_category_with_transactions(client, category_id):
    tx_id = client.post(TX, json=_payload(category_id)).json()["id"]

    assert client.delete(f"{CAT}/{category_id}").status_code == 409

    client.delete(f"{TX}/{tx_id}")
    assert client.delete(f"{CAT}/{category_id}").status_code == 204
