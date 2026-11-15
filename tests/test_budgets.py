from datetime import datetime, timezone


def test_create_budget(client):
    response = client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "Food"
    assert data["amount"] == 50000
    assert data["month"] == 11
    assert data["year"] == 2026


def test_create_duplicate_budget(client):
    payload = {
        "category": "Food",
        "amount": 50000,
        "month": 11,
        "year": 2026,
    }

    first = client.post("/api/v1/budgets", json=payload)
    second = client.post("/api/v1/budgets", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_create_budget_invalid_amount(client):
    response = client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 0,
            "month": 11,
            "year": 2026,
        },
    )

    assert response.status_code == 422


def test_create_budget_invalid_month(client):
    response = client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 13,
            "year": 2026,
        },
    )

    assert response.status_code == 422


def test_get_budgets(client):
    client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    response = client.get("/api/v1/budgets")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_budgets_by_month_and_year(client):
    client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    response = client.get("/api/v1/budgets?month=11&year=2026")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_budget_by_id(client):
    create_response = client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    budget_id = create_response.json()["id"]

    response = client.get(f"/api/v1/budgets/{budget_id}")

    assert response.status_code == 200
    assert response.json()["id"] == budget_id


def test_get_nonexistent_budget(client):
    response = client.get("/api/v1/budgets/999999")

    assert response.status_code == 404


def test_update_budget(client):
    create_response = client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    budget_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/budgets/{budget_id}",
        json={"amount": 60000},
    )

    assert response.status_code == 200
    assert response.json()["amount"] == 60000


def test_update_nonexistent_budget(client):
    response = client.patch(
        "/api/v1/budgets/999999",
        json={"amount": 60000},
    )

    assert response.status_code == 404


def test_delete_budget(client):
    create_response = client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    budget_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/budgets/{budget_id}")

    assert response.status_code == 204

    get_response = client.get(f"/api/v1/budgets/{budget_id}")

    assert get_response.status_code == 404


def test_delete_nonexistent_budget(client):
    response = client.delete("/api/v1/budgets/999999")

    assert response.status_code == 404


def test_budget_summary(client):
    client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    response = client.get("/api/v1/budgets/summary?month=11&year=2026")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"
    assert data[0]["budget_amount"] == 50000
    assert data[0]["spent"] == 0
    assert data[0]["remaining"] == 50000
    assert data[0]["percentage_used"] == 0
    assert data[0]["status"] == "within_budget"


def test_budget_summary_with_expenses(client):
    client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    transaction_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 30000,
            "transaction_type": "expense",
            "purpose": "Groceries",
            "category": "Food",
        },
    )

    assert transaction_response.status_code == 201

    response = client.get("/api/v1/budgets/summary?month=11&year=2026")

    assert response.status_code == 200

    data = response.json()[0]

    assert data["spent"] == 30000
    assert data["remaining"] == 20000
    assert data["percentage_used"] == 60
    assert data["status"] == "within_budget"


def test_budget_summary_near_limit(client):
    client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    client.post(
        "/api/v1/transactions",
        json={
            "amount": 45000,
            "transaction_type": "expense",
            "purpose": "Groceries",
            "category": "Food",
        },
    )

    response = client.get("/api/v1/budgets/summary?month=11&year=2026")

    assert response.status_code == 200

    assert response.json()[0]["status"] == "near_limit"


def test_budget_summary_exceeded(client):
    client.post(
        "/api/v1/budgets",
        json={
            "category": "Food",
            "amount": 50000,
            "month": 11,
            "year": 2026,
        },
    )

    client.post(
        "/api/v1/transactions",
        json={
            "amount": 60000,
            "transaction_type": "expense",
            "purpose": "Groceries",
            "category": "Food",
        },
    )

    response = client.get("/api/v1/budgets/summary?month=11&year=2026")

    assert response.status_code == 200

    data = response.json()[0]

    assert data["spent"] == 60000
    assert data["remaining"] == -10000
    assert data["percentage_used"] == 120
    assert data["status"] == "exceeded"
