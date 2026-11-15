def test_create_recurring_transaction(client):
    response = client.post(
        "/api/v1/recurring-transactions",
        json={
            "amount": 250000,
            "transaction_type": "income",
            "purpose": "Monthly salary",
            "category": "Salary",
            "frequency": "monthly",
            "start_date": "2026-11-01",
            "end_date": "2027-11-01",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == 250000
    assert data["transaction_type"] == "income"
    assert data["frequency"] == "monthly"
    assert data["next_run_date"] == "2026-11-01"
    assert data["is_active"] is True


def test_create_recurring_transaction_invalid_amount(client):
    response = client.post(
        "/api/v1/recurring-transactions",
        json={
            "amount": 0,
            "transaction_type": "expense",
            "purpose": "Rent",
            "frequency": "monthly",
            "start_date": "2026-11-01",
        },
    )

    assert response.status_code == 422


def test_create_recurring_transaction_invalid_frequency(client):
    response = client.post(
        "/api/v1/recurring-transactions",
        json={
            "amount": 10000,
            "transaction_type": "expense",
            "purpose": "Rent",
            "frequency": "biweekly",
            "start_date": "2026-11-01",
        },
    )

    assert response.status_code == 422


def test_create_recurring_transaction_invalid_dates(client):
    response = client.post(
        "/api/v1/recurring-transactions",
        json={
            "amount": 10000,
            "transaction_type": "expense",
            "purpose": "Rent",
            "frequency": "monthly",
            "start_date": "2026-12-01",
            "end_date": "2026-11-01",
        },
    )

    assert response.status_code == 422


def test_get_recurring_transactions(client):
    client.post(
        "/api/v1/recurring-transactions",
        json={
            "amount": 15000,
            "transaction_type": "expense",
            "purpose": "Internet subscription",
            "frequency": "monthly",
            "start_date": "2026-11-01",
        },
    )

    response = client.get("/api/v1/recurring-transactions")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_recurring_transaction_by_id(client):
    create_response = client.post(
        "/api/v1/recurring-transactions",
        json={
            "amount": 80000,
            "transaction_type": "expense",
            "purpose": "Monthly rent",
            "frequency": "monthly",
            "start_date": "2026-11-01",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.get(f"/api/v1/recurring-transactions/{transaction_id}")

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id


def test_get_nonexistent_recurring_transaction(client):
    response = client.get("/api/v1/recurring-transactions/999999")

    assert response.status_code == 404


def test_update_recurring_transaction(client):
    create_response = client.post(
        "/api/v1/recurring-transactions",
        json={
            "amount": 15000,
            "transaction_type": "expense",
            "purpose": "Internet subscription",
            "frequency": "monthly",
            "start_date": "2026-11-01",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/recurring-transactions/{transaction_id}",
        json={
            "amount": 20000,
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["amount"] == 20000
    assert response.json()["is_active"] is False


def test_update_nonexistent_recurring_transaction(client):
    response = client.patch(
        "/api/v1/recurring-transactions/999999",
        json={"amount": 20000},
    )

    assert response.status_code == 404


def test_delete_recurring_transaction(client):
    create_response = client.post(
        "/api/v1/recurring-transactions",
        json={
            "amount": 10000,
            "transaction_type": "expense",
            "purpose": "Subscription",
            "frequency": "monthly",
            "start_date": "2026-11-01",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/recurring-transactions/{transaction_id}")

    assert response.status_code == 204


def test_delete_nonexistent_recurring_transaction(client):
    response = client.delete("/api/v1/recurring-transactions/999999")

    assert response.status_code == 404
