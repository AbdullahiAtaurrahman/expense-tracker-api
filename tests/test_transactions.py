from fastapi import status


def test_get_transactions(client):
    response = client.get("/api/v1/transactions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_transaction_by_id(client):

    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.get(f"/api/v1/transactions/{transaction_id}")

    assert response.status_code == 200
    assert "created_at" in response.json()
    assert "updated_at" in response.json()
    assert create_response.json()["id"] == transaction_id
    assert create_response.json()["transaction_type"] == "income"
    assert create_response.json()["purpose"] == "Freelance project"


def test_create_transaction(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 2500,
            "transaction_type": "income",
            "purpose": "Freelance work",
        },
    )

    assert response.status_code == 201
    assert "created_at" in response.json()
    assert "updated_at" in response.json()

    assert "id" in response.json()


def test_create_transaction_with_negative_amount(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": -500,
            "transaction_type": "expense",
            "purpose": "Invalid transaction",
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_invalid_type(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 500,
            "transaction_type": "savings",
            "purpose": "Invalid transaction type",
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_long_purpose(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
            "purpose": "A" * 201,
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_empty_purpose(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
            "purpose": "",
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_zero_amount(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 0,
            "transaction_type": "expense",
            "purpose": "Zero amount",
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_missing_field(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
        },
    )

    assert response.status_code == 422


def test_update_transaction(client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={
            "amount": 2000,
            "purpose": "Completed freelance project",
        },
    )

    assert response.status_code == 200
    assert response.json()["amount"] == 2000
    assert response.json()["purpose"] == "Completed freelance project"
    assert response.json()["transaction_type"] == "income"


def test_update_nonexistent_transaction(client):

    response = client.patch(
        "/api/v1/transactions/999999",
        json={
            "amount": 2000,
        },
    )

    assert response.status_code == 404


def test_update_transaction_with_invalid_amount(client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={"amount": -200},
    )

    assert response.status_code == 422


def test_update_transaction_with_empty_purpose(client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={"purpose": ""},
    )

    assert response.status_code == 422


def test_update_transaction_with_invalid_type(client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={"transaction_type": "savings"},
    )

    assert response.status_code == 422


def test_delete_transaction(client):

    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "expense",
            "purpose": "Internet subscription",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/transactions/{transaction_id}")

    assert response.status_code == 204

    get_response = client.get(f"/api/v1/transactions/{transaction_id}")

    assert get_response.status_code == 404


def test_nonexistent_transaction(client):

    response = client.get("/api/v1/transactions/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction with ID 99999 not found"


def test_users_cannot_see_each_others_transactions(client, second_client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "User A transaction",
        },
    )

    assert create_response.status_code == 201

    response = second_client.get("/api/v1/transactions")

    assert response.status_code == 200
    assert response.json() == []


def test_user_cannot_access_another_users_transaction(client, second_client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "User A transaction",
        },
    )

    transaction_id = create_response.json()["id"]

    response = second_client.get(f"/api/v1/transactions/{transaction_id}")

    assert response.status_code == 404


def test_user_cannot_update_another_users_transaction(client, second_client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Original purpose",
        },
    )

    transaction_id = create_response.json()["id"]

    response = second_client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={
            "amount": 5000,
            "purpose": "Unauthorized update",
        },
    )

    assert response.status_code == 404

    original_response = client.get(f"/api/v1/transactions/{transaction_id}")

    assert original_response.status_code == 200
    assert original_response.json()["amount"] == 1500
    assert original_response.json()["purpose"] == "Original purpose"


def test_user_cannot_delete_another_users_transaction(client, second_client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "expense",
            "purpose": "User A subscription",
        },
    )

    transaction_id = create_response.json()["id"]

    response = second_client.delete(f"/api/v1/transactions/{transaction_id}")

    assert response.status_code == 404

    original_response = client.get(f"/api/v1/transactions/{transaction_id}")

    assert original_response.status_code == 200


def test_filter_income_transactions(client):
    client.post(
        "/api/v1/transactions",
        json={
            "amount": 5000,
            "transaction_type": "income",
            "purpose": "Salary",
        },
    )

    client.post(
        "/api/v1/transactions",
        json={
            "amount": 2000,
            "transaction_type": "expense",
            "purpose": "Groceries",
        },
    )

    response = client.get("/api/v1/transactions?transaction_type=income")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["transaction_type"] == "income"


def test_filter_expense_transactions(client):
    client.post(
        "/api/v1/transactions",
        json={
            "amount": 5000,
            "transaction_type": "income",
            "purpose": "Salary",
        },
    )

    client.post(
        "/api/v1/transactions",
        json={
            "amount": 2000,
            "transaction_type": "expense",
            "purpose": "Groceries",
        },
    )

    response = client.get("/api/v1/transactions?transaction_type=expense")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["transaction_type"] == "expense"


def test_filter_transactions_by_start_date(client):
    response = client.get(
        "/api/v1/transactions",
        params={"start_date": "2026-11-01T00:00:00"},
    )

    assert response.status_code == 200

    for transaction in response.json():
        assert transaction["created_at"] >= "2026-11-01T00:00:00"


def test_filter_transactions_by_end_date(client):
    response = client.get(
        "/api/v1/transactions",
        params={"end_date": "2026-11-13T23:59:59"},
    )

    assert response.status_code == 200

    for transaction in response.json():
        assert transaction["created_at"] <= "2026-11-13T23:59:59"


def test_filter_transactions_by_date_range(client):
    response = client.get(
        "/api/v1/transactions",
        params={
            "start_date": "2026-11-01T00:00:00",
            "end_date": "2026-11-13T23:59:59",
        },
    )

    assert response.status_code == 200

    for transaction in response.json():
        assert "2026-11-01T00:00:00" <= transaction["created_at"]
        assert transaction["created_at"] <= "2026-11-13T23:59:59"


def test_filter_transactions_by_date_and_type(client):
    response = client.get(
        "/api/v1/transactions",
        params={
            "transaction_type": "expense",
            "start_date": "2026-11-01T00:00:00",
            "end_date": "2026-11-13T23:59:59",
        },
    )

    assert response.status_code == 200

    for transaction in response.json():
        assert transaction["transaction_type"] == "expense"
        assert "2026-11-01T00:00:00" <= transaction["created_at"]
        assert transaction["created_at"] <= "2026-11-13T23:59:59"


def test_transactions_outside_date_range_are_excluded(client):
    response = client.get(
        "/api/v1/transactions",
        params={
            "start_date": "2030-01-01T00:00:00",
            "end_date": "2030-01-02T00:00:00",
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_filter_transactions_with_invalid_date(client):
    response = client.get(
        "/api/v1/transactions",
        params={"start_date": "invalid-date"},
    )

    assert response.status_code == 422


def test_filter_transactions_with_invalid_type(client):
    response = client.get(
        "/api/v1/transactions",
        params={"transaction_type": "invalid"},
    )

    assert response.status_code == 422


def test_get_transactions_with_default_pagination(client):
    response = client.get("/api/v1/transactions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 10


def test_get_transactions_with_limit(client):
    response = client.get(
        "/api/v1/transactions",
        params={"limit": 5},
    )

    assert response.status_code == 200
    assert len(response.json()) <= 5


def test_get_transactions_with_skip(client):
    response = client.get(
        "/api/v1/transactions",
        params={"skip": 5},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_transactions_with_skip_and_limit(client):
    response = client.get(
        "/api/v1/transactions",
        params={
            "skip": 5,
            "limit": 5,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) <= 5


def test_get_transactions_with_maximum_limit(client):
    response = client.get(
        "/api/v1/transactions",
        params={"limit": 100},
    )

    assert response.status_code == 200
    assert len(response.json()) <= 100


def test_get_transactions_with_zero_skip(client):
    response = client.get(
        "/api/v1/transactions",
        params={"skip": 0},
    )

    assert response.status_code == 200


def test_get_transactions_with_negative_skip(client):
    response = client.get(
        "/api/v1/transactions",
        params={"skip": -1},
    )

    assert response.status_code == 422


def test_get_transactions_with_zero_limit(client):
    response = client.get(
        "/api/v1/transactions",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_get_transactions_with_negative_limit(client):
    response = client.get(
        "/api/v1/transactions",
        params={"limit": -5},
    )

    assert response.status_code == 422


def test_get_transactions_with_limit_above_maximum(client):
    response = client.get(
        "/api/v1/transactions",
        params={"limit": 101},
    )

    assert response.status_code == 422


def test_get_transactions_with_pagination_and_type_filter(client):
    response = client.get(
        "/api/v1/transactions",
        params={
            "transaction_type": "expense",
            "skip": 0,
            "limit": 5,
        },
    )

    assert response.status_code == 200

    for transaction in response.json():
        assert transaction["transaction_type"] == "expense"


def test_get_transactions_with_pagination_and_sorting(client):
    response = client.get(
        "/api/v1/transactions",
        params={
            "sort_by": "amount",
            "order": "asc",
            "skip": 0,
            "limit": 5,
        },
    )

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) <= 5

    amounts = [transaction["amount"] for transaction in transactions]

    assert amounts == sorted(amounts)


def test_get_transactions_with_large_skip(client):
    response = client.get(
        "/api/v1/transactions",
        params={
            "skip": 100000,
            "limit": 10,
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_transaction_summary(client):
    response = client.get("/api/v1/transactions/summary")

    assert response.status_code == 200

    data = response.json()

    assert "total_income" in data
    assert "total_expenses" in data
    assert "balance" in data
    assert "total_transactions" in data
    assert "income_transactions" in data
    assert "expense_transactions" in data

    assert data["balance"] == (data["total_income"] - data["total_expenses"])


def test_transaction_summary_with_no_transactions(client):
    future_start = "2030-01-01T00:00:00"
    future_end = "2030-01-02T00:00:00"

    response = client.get(
        "/api/v1/transactions/summary",
        params={
            "start_date": future_start,
            "end_date": future_end,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_income"] == 0
    assert data["total_expenses"] == 0
    assert data["balance"] == 0
    assert data["total_transactions"] == 0
    assert data["income_transactions"] == 0
    assert data["expense_transactions"] == 0


def test_transaction_summary_with_date_range(client):
    response = client.get(
        "/api/v1/transactions/summary",
        params={
            "start_date": "2026-11-01T00:00:00",
            "end_date": "2026-11-30T23:59:59",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_income"] >= 0
    assert data["total_expenses"] >= 0
    assert data["total_transactions"] >= 0


def test_transaction_summary_with_invalid_date(client):
    response = client.get(
        "/api/v1/transactions/summary",
        params={"start_date": "invalid-date"},
    )

    assert response.status_code == 422


def test_transaction_summary_balance_calculation(client):
    response = client.get("/api/v1/transactions/summary")

    assert response.status_code == 200

    data = response.json()

    expected_balance = data["total_income"] - data["total_expenses"]

    assert data["balance"] == expected_balance


def test_transaction_summary_transaction_counts(client):
    response = client.get("/api/v1/transactions/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_transactions"] == (
        data["income_transactions"] + data["expense_transactions"]
    )


def test_get_monthly_analytics(client):
    response = client.get("/api/v1/transactions/analytics/monthly")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_monthly_analytics_response_structure(client):
    response = client.get("/api/v1/transactions/analytics/monthly")

    assert response.status_code == 200

    for month in response.json():
        assert "month" in month
        assert "total_income" in month
        assert "total_expenses" in month
        assert "balance" in month
        assert "income_transactions" in month
        assert "expense_transactions" in month
        assert "total_transactions" in month


def test_monthly_analytics_balance_calculation(client):
    response = client.get("/api/v1/transactions/analytics/monthly")

    assert response.status_code == 200

    for month in response.json():
        assert month["balance"] == (month["total_income"] - month["total_expenses"])


def test_monthly_analytics_transaction_counts(client):
    response = client.get("/api/v1/transactions/analytics/monthly")

    assert response.status_code == 200

    for month in response.json():
        assert month["total_transactions"] == (
            month["income_transactions"] + month["expense_transactions"]
        )


def test_monthly_analytics_chronological_order(client):
    response = client.get("/api/v1/transactions/analytics/monthly")

    assert response.status_code == 200

    months = [month["month"] for month in response.json()]

    assert months == sorted(months)


def test_monthly_analytics_with_date_range(client):
    response = client.get(
        "/api/v1/transactions/analytics/monthly",
        params={
            "start_date": "2026-11-01T00:00:00",
            "end_date": "2026-11-30T23:59:59",
        },
    )

    assert response.status_code == 200

    for month in response.json():
        assert "2026-11" == month["month"]


def test_monthly_analytics_with_invalid_date(client):
    response = client.get(
        "/api/v1/transactions/analytics/monthly",
        params={
            "start_date": "invalid-date",
        },
    )

    assert response.status_code == 422


def test_monthly_analytics_with_empty_date_range(client):
    response = client.get(
        "/api/v1/transactions/analytics/monthly",
        params={
            "start_date": "2030-01-01T00:00:00",
            "end_date": "2030-01-02T00:00:00",
        },
    )

    assert response.status_code == 200
    assert response.json() == []
