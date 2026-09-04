"""Tests de los endpoints de reportes."""

from decimal import Decimal

TX = "/api/v1/transactions"
CAT = "/api/v1/categories"
BUD = "/api/v1/budgets"
REPORTS = "/api/v1/reports"


def _create_transaction(client, category_id, **overrides):
    data = {
        "amount": "100.00",
        "type": "expense",
        "occurred_on": "2026-09-15",
        "category_id": category_id,
    }
    data.update(overrides)
    return client.post(TX, json=data)


def test_summary_totals_income_and_expense(client, category_id):
    _create_transaction(client, category_id, type="income", amount="1000")
    _create_transaction(client, category_id, type="expense", amount="300")
    _create_transaction(client, category_id, type="expense", amount="50")
    # Fuera del mes que vamos a consultar: no debe contar.
    _create_transaction(
        client, category_id, type="expense", amount="9999", occurred_on="2026-08-01"
    )

    response = client.get(f"{REPORTS}/summary", params={"month": "2026-09"})
    assert response.status_code == 200
    body = response.json()
    assert Decimal(str(body["total_income"])) == Decimal("1000")
    assert Decimal(str(body["total_expense"])) == Decimal("350")
    assert Decimal(str(body["balance"])) == Decimal("650")


def test_summary_with_no_transactions_returns_zeros(client):
    response = client.get(f"{REPORTS}/summary", params={"month": "2026-01"})
    body = response.json()
    assert Decimal(str(body["total_income"])) == 0
    assert Decimal(str(body["total_expense"])) == 0
    assert Decimal(str(body["balance"])) == 0


def test_summary_rejects_bad_month_format(client):
    assert client.get(f"{REPORTS}/summary", params={"month": "septiembre"}).status_code == 422


def test_by_category_groups_and_sorts_by_total(client, category_id):
    transporte_id = client.post(CAT, json={"name": "Transporte"}).json()["id"]
    _create_transaction(client, category_id, amount="50")
    _create_transaction(client, category_id, amount="30")
    _create_transaction(client, transporte_id, amount="200")

    response = client.get(f"{REPORTS}/by-category", params={"month": "2026-09"})
    body = response.json()
    assert body[0]["category_name"] == "Transporte"
    assert Decimal(str(body[0]["total"])) == Decimal("200")
    assert body[1]["category_name"] == "Comida"
    assert Decimal(str(body[1]["total"])) == Decimal("80")


def test_by_category_can_filter_by_type(client, category_id):
    _create_transaction(client, category_id, type="income", amount="1000")
    _create_transaction(client, category_id, type="expense", amount="40")

    params = {"month": "2026-09", "type": "income"}
    result = client.get(f"{REPORTS}/by-category", params=params).json()
    assert len(result) == 1
    assert Decimal(str(result[0]["total"])) == Decimal("1000")


def test_budget_status_flags_when_over_budget(client, category_id):
    client.post(BUD, json={"category_id": category_id, "month": "2026-09", "limit_amount": "100"})
    _create_transaction(client, category_id, amount="60")

    response = client.get(f"{REPORTS}/budget-status", params={"month": "2026-09"})
    body = response.json()
    assert len(body) == 1
    assert Decimal(str(body[0]["spent"])) == Decimal("60")
    assert Decimal(str(body[0]["remaining"])) == Decimal("40")
    assert body[0]["over_budget"] is False

    _create_transaction(client, category_id, amount="60")  # ahora van 120, limite 100
    response = client.get(f"{REPORTS}/budget-status", params={"month": "2026-09"})
    body = response.json()
    assert Decimal(str(body[0]["spent"])) == Decimal("120")
    assert body[0]["over_budget"] is True


def test_budget_status_only_lists_categories_with_a_budget(client, category_id):
    transporte_id = client.post(CAT, json={"name": "Transporte"}).json()["id"]
    client.post(BUD, json={"category_id": category_id, "month": "2026-09", "limit_amount": "100"})
    # Transporte tiene gasto pero NO presupuesto: no debe aparecer.
    _create_transaction(client, transporte_id, amount="500")

    response = client.get(f"{REPORTS}/budget-status", params={"month": "2026-09"})
    body = response.json()
    assert len(body) == 1
    assert body[0]["category_id"] == category_id
