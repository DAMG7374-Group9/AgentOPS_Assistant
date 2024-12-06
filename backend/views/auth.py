from fastapi import APIRouter, HTTPException
from starlette import status

from backend.schemas import ExceptionSchema
from backend.schemas.auth import Token, Credentials, RefreshToken
from backend.services.auth import (
    authenticate_user,
    generate_token,
    authenticate_refresh_token,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/token",
    response_model=Token,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def token(credentials: Credentials) -> Token | HTTPException:
    if user := await authenticate_user(
        username=credentials.username, password=credentials.password
    ):
        return await generate_token(user)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )


@auth_router.post(
    "/refresh",
    response_model=Token,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def refresh_token(request: RefreshToken) -> Token | HTTPException:
    if new_tokens := await authenticate_refresh_token(token=request.refresh_token):
        return new_tokens
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
    )
