import pytest
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from src.settings import settings
from typing import Dict

from src.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_access_token,
)
from fastapi import HTTPException, status


def test_get_password_hash():
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_verify_password():
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed)  # assert it's True
    assert not verify_password("wrongpassword", hashed)  # assert it's False


def test_create_access_token():
    data: Dict[str, str | datetime] = {"sub": "1", "username": "testuser"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0
    assert settings.SECRET_KEY

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == "1"
        assert payload["username"] == "testuser"
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
    except JWTError:
        pytest.fail("Failed to decode JWT token")


def test_verify_access_token_valid():
    data: Dict[str, str | datetime] = {"sub": "1", "username": "testuser"}
    token = create_access_token(data)

    payload = verify_access_token(token)
    assert payload["sub"] == "1"
    assert payload["username"] == "testuser"


def test_verify_access_token_invalid():
    invalid_token = "invalid.token.string"

    with pytest.raises(HTTPException) as info:
        _ = verify_access_token(invalid_token)

    assert info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in info.value.detail


def test_verify_access_token_expired():
    data: Dict[str, str | datetime] = {"sub": "1", "username": "testuser"}
    # create token that expired 1 minute ago
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    assert settings.SECRET_KEY

    expired_token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    with pytest.raises(HTTPException) as info:
        _ = verify_access_token(expired_token)

    assert info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in info.value.detail


def test_verify_access_token_missing_sub():
    data: Dict[str, str | datetime] = {"username": "testuser"}  # no 'sub'
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    assert settings.SECRET_KEY

    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    with pytest.raises(HTTPException) as info:
        _ = verify_access_token(token)

    assert info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in info.value.detail
