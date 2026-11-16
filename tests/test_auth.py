from fastapi import status


def test_inactive_user_cannot_login(client, deactivate_default_test_user):
    deactivate_default_test_user()

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"


def test_inactive_user_cannot_access_protected_route(
    client, deactivate_default_test_user
):
    deactivate_default_test_user()

    response = client.get("/api/v1/transactions")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_created_at_is_saved(client, get_user_by_email):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "timestamp@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = get_user_by_email("timestamp@example.com")

    assert user is not None
    assert user.created_at is not None


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "newuser@example.com"
    assert "hashed_password" not in response.json()


def test_register_user_with_existing_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_register_user_with_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "securepassword123",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_register_user_with_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "short",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_login_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


def test_login_with_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_with_unregistered_email(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_access_transactions_without_token():
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get("/api/v1/transactions")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_access_transactions_with_invalid_token():
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(
        app,
        headers={"Authorization": "Bearer invalid.token.value"},
    ) as unauthenticated_client:
        response = unauthenticated_client.get("/api/v1/transactions")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
