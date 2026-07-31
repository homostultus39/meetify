import pytest
from unittest.mock import AsyncMock, patch
from fastapi.security import HTTPAuthorizationCredentials

from api.deps.get_current_user import get_current_user
from api.exceptions.auth import TokenExpiredError, TokenInvalidError
from api.exceptions.user import UserNotFoundError


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_success(self, mock_user_model):
        payload = {
            "sub": str(mock_user_model.id),
            "type": "access"
        }

        with patch("api.deps.get_current_user.TokenService.decode_token", return_value=payload):
            with patch("api.deps.get_current_user.get_user_by_user_id", new_callable=AsyncMock, return_value=mock_user_model):
                credentials = HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials="some_valid_token"
                )
                result = await get_current_user(
                    session=AsyncMock(),
                    credentials=credentials
                )
                assert result["user_id"] == mock_user_model.id
                assert result["username"] == mock_user_model.username
                assert result["role"] == mock_user_model.role

    @pytest.mark.asyncio
    async def test_invalid_token(self, mock_user_model):
        payload = {
            "sub": str(mock_user_model.id),
            "type": "refresh"
        }
        with patch("api.deps.get_current_user.TokenService.decode_token", return_value=payload):
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="some_token"
            )
            with pytest.raises(TokenInvalidError) as exc:
                await get_current_user(session=AsyncMock(), credentials=credentials)
            assert str(exc.value) == "Invalid type of token"

    @pytest.mark.asyncio
    async def test_token_expired(self):
        with patch("api.deps.get_current_user.TokenService.decode_token", side_effect=TokenExpiredError("Token has expired")):
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="some_expired_token"
            )
            with pytest.raises(TokenExpiredError) as exc:
                await get_current_user(session=AsyncMock(), credentials=credentials)
            assert str(exc.value) == "Token has expired"

    @pytest.mark.asyncio
    async def test_user_not_found(self, mock_user_model):
        payload = {
            "sub": str(mock_user_model.id),
            "type": "access"
        }
        with patch("api.deps.get_current_user.TokenService.decode_token", return_value=payload):
            with patch(
                "api.deps.get_current_user.get_user_by_user_id",
                new_callable=AsyncMock,
                return_value=None
            ):
                credentials = HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials="some_valid_token"
                )
                with pytest.raises(UserNotFoundError) as exc:
                    await get_current_user(session=AsyncMock(), credentials=credentials)
                assert "User with id" in str(exc.value)