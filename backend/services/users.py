import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.database import db_session
from backend.database.users import UserModel
from backend.schemas.users import UserRequest, UserCreateRequest

logger = logging.getLogger(__name__)


async def _create_user(user: UserRequest) -> Optional[UserModel]:
    """
    Create a new user in the database.

    Args:
        user: UserRequest object containing user details

    Returns:
        UserModel if creation successful, None if user already exists or on error
    """
    try:
        # Using synchronous context manager
        with db_session() as session:
            # Convert the request to a UserCreateRequest for password hashing
            user_create = UserCreateRequest(**user.model_dump())

            # Create new user instance excluding id field
            user_dict = user_create.model_dump(
                exclude={"id"} if "id" in user_create.model_dump() else set()
            )
            new_user = UserModel(**user_dict)

            # Add and commit
            session.add(new_user)
            session.commit()

            # Refresh to get the generated ID and timestamps
            session.refresh(new_user)
            return new_user

    except IntegrityError as ie:
        logger.error(f"User creation failed - integrity error: {str(ie)}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}", exc_info=True)
        return None


async def _get_user(username: str) -> Optional[UserModel]:
    """
    Retrieve a user by username.

    Args:
        username: Username to look up

    Returns:
        UserModel if found, None if not found or on error
    """
    try:
        # Using synchronous context manager
        with db_session() as session:
            # Use select to query the user
            stmt = select(UserModel).where(UserModel.username == username)

            # Execute query and return first result or None
            result = session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Ensure the instance is attached to this session
                session.refresh(user)

            return user

    except Exception as e:
        logger.error(f"Error fetching user {username}: {str(e)}", exc_info=True)
        return None


async def _update_user(username: str, update_data: dict) -> Optional[UserModel]:
    """
    Update user details.

    Args:
        username: Username of user to update
        update_data: Dictionary of fields to update

    Returns:
        Updated UserModel if successful, None if user not found or on error
    """
    try:
        with db_session() as session:
            # Get existing user
            stmt = select(UserModel).where(UserModel.username == username)
            result = session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return None

            # Update fields
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            session.commit()
            session.refresh(user)
            return user

    except IntegrityError as ie:
        logger.error(f"User update failed - integrity error: {str(ie)}")
        return None

    except Exception as e:
        logger.error(f"Error updating user {username}: {str(e)}", exc_info=True)
        return None


async def _delete_user(username: str) -> bool:
    """
    Delete a user from the database.

    Args:
        username: Username of user to delete

    Returns:
        True if user was deleted, False if user not found or on error
    """
    try:
        with db_session() as session:
            stmt = select(UserModel).where(UserModel.username == username)
            result = session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return False

            session.delete(user)
            session.commit()
            return True

    except Exception as e:
        logger.error(f"Error deleting user {username}: {str(e)}", exc_info=True)
        return False