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
