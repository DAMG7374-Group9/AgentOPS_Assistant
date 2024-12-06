from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from sqlalchemy import select

from backend.config import settings
from backend.database import db_session
from backend.database.users import UserModel
from backend.schemas.auth import Token
from backend.utils import verify_password


async def authenticate_user(username: str, password: str) -> Optional[UserModel]:
    with db_session() as session:
        user = session.scalar(select(UserModel).filter_by(username=username))
        if user and verify_password(
            plain_password=password, hashed_password=user.password
        ):
            return await validate_user(user=user)
    return None


async def validate_user(user: UserModel) -> UserModel:
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account is deactivated.",
        )
    return user


async def generate_token(user: UserModel) -> Token:
    _access_token = {
        "user_id": user.id,
        "password_timestamp": user.password_timestamp,
        "exp": datetime.utcnow()
        + timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRATION_SECONDS),
        "token_type": "access",
    }
    _refresh_token = _access_token.copy() | {
        "exp": datetime.utcnow()
        + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRATION_SECONDS),
        "token_type": "refresh",
    }

    access_token, refresh_token = map(
        lambda x: jwt.encode(x, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM),
        (_access_token, _refresh_token),
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


async def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM
        )
    except (JWTError, ExpiredSignatureError, JWTClaimsError):
        return {}


async def authenticate_token(
    user_id: int, password_timestamp: float
) -> UserModel | None:
    """
    Authenticate a user by id and password timestamp. Check if the token matches the latest generated token (using
    the timestamp). If it does not match, then the token is invalidated.
    :param user_id:
    :param password_timestamp:
    :return:
    """
    with db_session() as session:
        user = session.get(UserModel, user_id)
        if user and password_timestamp == user.password_timestamp:
            return await validate_user(user=user)
    return None


async def authenticate_refresh_token(token: str) -> Token | None:
    payload = await decode_token(token)
    if payload and payload.get("token_type") == "refresh":
        if user := await authenticate_token(
            user_id=payload["user_id"], password_timestamp=payload["password_timestamp"]
        ):
            return await generate_token(user)
    return None
