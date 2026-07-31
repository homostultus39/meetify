import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
import jwt

from api.auth.management.token_service import TokenService
from api.exceptions.auth import TokenExpiredError, TokenInvalidError


class TestTokenService:
    def test_decode_token_valid(self, mock_settings):
        payload = {"sub": "123", "type": "access"}
        token = jwt.encode(payload, mock_settings.secret_key, algorithm=mock_settings.algorithm)
        with patch("api.auth.management.token_service.settings", mock_settings):
            decoded = TokenService.decode_token(token)
            assert decoded["sub"] == "123"
            assert decoded["type"] == "access"

    def test_decode_token_expired(self, mock_settings):
        exp_timestamp = int((datetime.now() - timedelta(days=1)).timestamp())
        payload = {"sub": "123", "exp": exp_timestamp}
        token = jwt.encode(payload, mock_settings.secret_key, algorithm=mock_settings.algorithm)
        with patch("api.auth.management.token_service.settings", mock_settings):
            with pytest.raises(TokenExpiredError):
                TokenService.decode_token(token)

    def test_decode_token_invalid(self, mock_settings):
        token = "some_invalid_token"
        with patch("api.auth.management.token_service.settings", mock_settings):
            with pytest.raises(TokenInvalidError):
                TokenService.decode_token(token)

    @pytest.mark.asyncio
    async def test_reset_token_pair_without_blocking(self, mock_user_model, mock_settings):
        with patch("api.auth.management.token_service.settings", mock_settings):
            with patch("api.auth.management.token_service.TokenRepository.set_record", new_callable=AsyncMock) as mock_set:
                result = await TokenService.reset_token_pair(mock_user_model)
                assert "access_token" in result
                assert "refresh_token" in result
                mock_set.assert_not_called()

    @pytest.mark.asyncio
    async def test_reset_token_pair_with_blocking(self, mock_user_model, mock_settings):
        exp_timestamp = int((datetime.now() + timedelta(days=1)).timestamp())
        old_refresh_payload = {
            "sub": str(mock_user_model.id),
            "exp": exp_timestamp,
            "jti": "old_jti",
            "type": "refresh"
        }
        old_refresh_token = jwt.encode(old_refresh_payload, mock_settings.secret_key, algorithm=mock_settings.algorithm)

        with patch("api.auth.management.token_service.settings", mock_settings):
            with patch("api.auth.management.token_service.TokenRepository.set_record", new_callable=AsyncMock) as mock_set:
                result = await TokenService.reset_token_pair(mock_user_model, exp_refresh_token=old_refresh_token)
                mock_set.assert_called_once_with(jti="old_jti", ttl_seconds=exp_timestamp)
                assert "access_token" in result
                assert "refresh_token" in result

    @pytest.mark.asyncio
    async def test_reset_token_pair_uses_settings(self, mock_user_model, mock_settings):
        with patch("api.auth.management.token_service.settings", mock_settings):
            with patch("api.auth.management.token_service.TokenRepository.set_record", new_callable=AsyncMock):
                result = await TokenService.reset_token_pair(mock_user_model)
                access_decoded = jwt.decode(result["access_token"], mock_settings.secret_key, algorithms=[mock_settings.algorithm])
                refresh_decoded = jwt.decode(result["refresh_token"], mock_settings.secret_key, algorithms=[mock_settings.algorithm])
                assert access_decoded["type"] == "access"
                assert refresh_decoded["type"] == "refresh"
                assert access_decoded["sub"] == str(mock_user_model.id)
                assert refresh_decoded["sub"] == str(mock_user_model.id)
                assert "exp" in access_decoded
                assert "exp" in refresh_decoded

    @pytest.mark.asyncio
    async def test_block_token(self, mock_user_model, mock_settings):
        exp_timestamp = int((datetime.now() + timedelta(days=1)).timestamp())
        refresh_payload = {
            "sub": str(mock_user_model.id),
            "exp": exp_timestamp,
            "jti": "jti_to_block",
            "type": "refresh"
        }
        refresh_token = jwt.encode(refresh_payload, mock_settings.secret_key, algorithm=mock_settings.algorithm)

        with patch("api.auth.management.token_service.settings", mock_settings):
            with patch("api.auth.management.token_service.TokenRepository.set_record", new_callable=AsyncMock) as mock_set:
                await TokenService.block_token(refresh_token)
                mock_set.assert_called_once_with(jti="jti_to_block", ttl_seconds=exp_timestamp)