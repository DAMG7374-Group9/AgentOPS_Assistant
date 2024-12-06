from fastapi import APIRouter, status, HTTPException

from backend.database.users import UserModel
from backend.schemas import ExceptionSchema
from backend.schemas.users import UserRequest, UserResponse
from backend.services.users import _create_user, _get_user  # Added _get_user import

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.post(
    "/",
    response_model=UserResponse,
    responses={status.HTTP_409_CONFLICT: {"model": ExceptionSchema}},
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserRequest) -> UserModel:
    print(user)
    if created_user := await _create_user(user=user):
        return created_user
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"UserModel `{user.username}` already exists",
    )


@users_router.get(
    "/",
    response_model=UserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
    },
)
async def get_user(username: str) -> UserResponse:
    if user := await _get_user(username=username):
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with username '{username}' not found",
    )
