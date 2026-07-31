import pytest
from uuid import uuid4
from api.auth.management.pwd_manager import PWDManager
from services.database.enums import UserRoles


class TestAuth:
    @pytest.mark.asyncio
    async def test_login_success(self, async_client, create_user_in_db):
        user_id = str(uuid4())
        password = "some_secret"
        hashed = PWDManager.hash_password(password)
        await create_user_in_db(user_id, "testuser", hashed, UserRoles.STAFF.value)

        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": password}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in response.cookies

    # async def test_login_wrong_password(self, async_client, create_user_in_db):
    #     user_id = str(uuid4())
    #     password = "correct"
    #     hashed = PWDManager.hash_password(password)
    #     await create_user_in_db(user_id, "testuser", hashed, UserRoles.USER.value)

    #     response = await async_client.post(
    #         "/api/v1/auth/login",
    #         json={"username": "testuser", "password": "wrong"}
    #     )
    #     assert response.status_code == 401
    #     assert response.json()["detail"] == "Invalid credentials"

    # async def test_login_user_not_found(self, async_client):
    #     response = await async_client.post(
    #         "/api/v1/auth/login",
    #         json={"username": "nonexistent", "password": "any"}
    #     )
    #     assert response.status_code == 401
    #     assert response.json()["detail"] == "Invalid credentials"

    # async def test_refresh_success(self, async_client, create_user_in_db):
    #     # 1. Создаём пользователя и логинимся
    #     user_id = str(uuid4())
    #     password = "secret"
    #     hashed = PWDManager.hash_password(password)
    #     await create_user_in_db(user_id, "testuser", hashed, UserRoles.USER.value)

    #     login_resp = await async_client.post(
    #         "/api/v1/auth/login",
    #         json={"username": "testuser", "password": password}
    #     )
    #     assert login_resp.status_code == 200
    #     refresh_token = login_resp.cookies.get("refresh_token")

    #     # 2. Отправляем запрос на обновление
    #     refresh_resp = await async_client.post(
    #         "/api/v1/auth/refresh",
    #         cookies={"refresh_token": refresh_token}
    #     )
    #     assert refresh_resp.status_code == 200
    #     data = refresh_resp.json()
    #     assert "access_token" in data
    #     # Проверяем, что новый refresh_token установлен
    #     new_refresh = refresh_resp.cookies.get("refresh_token")
    #     assert new_refresh is not None
    #     assert new_refresh != refresh_token  # должен быть новый токен

    # async def test_refresh_missing_token(self, async_client):
    #     response = await async_client.post("/api/v1/auth/refresh")
    #     assert response.status_code == 401
    #     assert response.json()["detail"] == "Refresh token missing"

    # async def test_refresh_invalid_token(self, async_client):
    #     # Устанавливаем заведомо невалидный токен
    #     response = await async_client.post(
    #         "/api/v1/auth/refresh",
    #         cookies={"refresh_token": "invalid.token"}
    #     )
    #     assert response.status_code == 401
    #     # Ожидаем одну из ошибок: Invalid token или Token expired (в зависимости от кода)
    #     assert "Invalid token" in response.json()["detail"] or "Token has expired" in response.json()["detail"]

    # async def test_logout_success(self, async_client, create_user_in_db):
    #     # Создаём пользователя и логинимся
    #     user_id = str(uuid4())
    #     password = "secret"
    #     hashed = PWDManager.hash_password(password)
    #     await create_user_in_db(user_id, "testuser", hashed, UserRoles.USER.value)

    #     login_resp = await async_client.post(
    #         "/api/v1/auth/login",
    #         json={"username": "testuser", "password": password}
    #     )
    #     refresh_token = login_resp.cookies.get("refresh_token")

    #     # Выход
    #     logout_resp = await async_client.post(
    #         "/api/v1/auth/logout",
    #         cookies={"refresh_token": refresh_token}
    #     )
    #     assert logout_resp.status_code == 200
    #     assert logout_resp.json()["message"] == "Logged out successfully"
    #     # Проверяем, что cookie удалена
    #     assert "refresh_token" not in logout_resp.cookies or logout_resp.cookies.get("refresh_token") == ""

    #     # Проверяем, что refresh_token теперь заблокирован – попытка обновить должна упасть
    #     refresh_resp = await async_client.post(
    #         "/api/v1/auth/refresh",
    #         cookies={"refresh_token": refresh_token}
    #     )
    #     assert refresh_resp.status_code == 401
    #     # Ожидаем, что токен истёк или невалиден (заблокирован -> TokenExpiredError)
    #     assert "Token has expired" in refresh_resp.json()["detail"] or "Invalid token" in refresh_resp.json()["detail"]

    # async def test_logout_without_token(self, async_client):
    #     response = await async_client.post("/api/v1/auth/logout")
    #     assert response.status_code == 200
    #     assert response.json()["message"] == "Logged out successfully"
    #     # Кука уже удалена, ничего страшного

    # async def test_logout_with_invalid_token(self, async_client):
    #     response = await async_client.post(
    #         "/api/v1/auth/logout",
    #         cookies={"refresh_token": "invalid.token"}
    #     )
    #     assert response.status_code == 200
    #     assert response.json()["message"] == "Logged out successfully"
    #     # Кука удалена
    #     assert "refresh_token" not in response.cookies or response.cookies.get("refresh_token") == ""