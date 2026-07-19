import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.dependencies import get_current_user
from src.database import User
from jose import JWTError


def test_get_current_user_valid_token():
    mock_db = Mock(spec=Session)

    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.username = "testuser"

    with patch("src.dependencies.verify_access_token") as mock_verify:
        mock_verify.return_value = {"sub": "1"}
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        user = get_current_user(token="valid_token", db=mock_db)

        assert user == mock_user

        mock_verify.assert_called_once_with("valid_token")
        mock_db.query.assert_called_once_with(User)
        mock_db.query.return_value.filter.assert_called_once()
        mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_current_user_invalid_token():
    mock_db = Mock(spec=Session)

    with patch("src.dependencies.verify_access_token") as mock_verify:
        mock_verify.side_effect = JWTError("Invalid token")
        with pytest.raises(HTTPException) as info:
            _ = get_current_user(token="invalid_token", db=mock_db)

        assert info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in info.value.detail


def test_get_current_user_missing_sub():
    mock_db = Mock(spec=Session)

    with patch("src.dependencies.verify_access_token") as mock_verify:
        mock_verify.return_value = {"username": "testuser"}  # no 'sub'

        with pytest.raises(HTTPException) as info:
            _ = get_current_user(token="invalid_token", db=mock_db)

        assert info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in info.value.detail


def test_get_current_user_user_not_found():
    mock_db = Mock(spec=Session)

    with patch("src.dependencies.verify_access_token") as mock_verify:
        mock_verify.return_value = {"sub": "999"}
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as info:
            _ = get_current_user(token="valid_token", db=mock_db)

        assert info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in info.value.detail
