
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    # Register first
    register_payload = {
        "email": "login_test@example.com",
        "password": "password123",
        "full_name": "Login Test"
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    # Login
    login_data = {
        "username": "login_test@example.com",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/auth/login/access-token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_read_users_me(async_client: AsyncClient):
    # Register
    email = "me_test@example.com"
    password = "password123"
    register_payload = {
        "email": email,
        "password": password,
        "full_name": "Me Test"
    }
    await async_client.post("/api/v1/auth/register", json=register_payload)

    # Login
    login_data = {
        "username": email,
        "password": password
    }
    login_res = await async_client.post("/api/v1/auth/login/access-token", data=login_data)
    token = login_res.json()["access_token"]

    # Get User Me
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
