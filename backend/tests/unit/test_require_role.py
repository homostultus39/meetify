import pytest
from unittest.mock import patch

from api.deps.require_role import require_role
from api.exceptions.permission import PermissionDeniedError
from services.database.enums import UserRoles


class TestRequireRole:
    @pytest.mark.asyncio
    async def test_permission_allowed(self, mock_user_model):
        payload = {
            "user_id": str(mock_user_model.id),
            "username": mock_user_model.username,
            "role": mock_user_model.role.value,
        }

        with patch("api.deps.require_role.get_current_user", return_value=payload):
            checker = require_role(UserRoles.ADMIN)
            result = await checker(user=payload)
            assert result == payload

    @pytest.mark.asyncio
    async def test_permission_denied(self, mock_user_model):
        payload = {
            "user_id": str(mock_user_model.id),
            "username": mock_user_model.username,
            "role": UserRoles.STAFF.value,
        }
        checker = require_role(UserRoles.ADMIN)
        with pytest.raises(PermissionDeniedError) as exc:
            await checker(user=payload)
        assert "Insufficient permissions" in str(exc.value)

    @pytest.mark.asyncio
    async def test_multiple_allowed_roles(self, mock_user_model):
        payload = {
            "user_id": str(mock_user_model.id),
            "username": mock_user_model.username,
            "role": mock_user_model.role.value,
        }
        checker = require_role(UserRoles.ADMIN, UserRoles.STAFF)
        result = await checker(user=payload)
        assert result == payload