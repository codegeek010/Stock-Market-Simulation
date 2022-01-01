import json
import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import Session

from common.authentication import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from common.constants import (
    USERNAME_EXISTS,
    USER_CREATED,
    WRONG_CREDENTIALS,
    NO_DATA_FOUND,
)
from common.helpers import redis_client
from database.db import get_db
from models.user import UserMethods
from schemas.users_schema import (
    UserRequestLoginSchema,
    UserRequestSchema,
    UserResponseSchema,
)

user_router = APIRouter(
    prefix="/users",
    responses={404: {"description": "Not found"}},
)


@user_router.post("/create", response_model=UserResponseSchema)
async def create_user(
    user: UserRequestSchema, db: Session = Depends(get_db)
) -> ORJSONResponse:
    """
    Sign up as new User.

    Args:
        user: UserRequestSchema
        db: Session

    Returns:
        User
    """
    user_check = UserMethods.get_record_with_(db, username=user.username)
    if user_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=USERNAME_EXISTS
        )
    user_data = user.model_dump()
    user_data["id"] = str(uuid.uuid4())
    user_data["password"] = get_password_hash(user.password)
    UserMethods.create_record(user_data, db)
    db.commit()

    return ORJSONResponse(content={"message": USER_CREATED}, status_code=200)


@user_router.post("/login")
async def login_user(
    user: UserRequestLoginSchema, db: Session = Depends(get_db)
) -> ORJSONResponse:
    """
    Login user if the provided creds are correct.

    Args:
        user: UserRequestLoginSchema
        db: Session

    Returns:
        Dict
    """
    user_data = await authenticate_user(
        username=user.username, password=user.password, db=db
    )
    if not user_data:
        raise HTTPException(detail=WRONG_CREDENTIALS, status_code=400)
    access_token = create_access_token(
        data={
            "id": user_data.id,
            "username": user_data.username,
        }
    )
    token_data = {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
    }
    return ORJSONResponse(content={"data": token_data}, status_code=200)


@user_router.get("/{username}")
async def get_user_data(username: str, db: Session = Depends(get_db)) -> ORJSONResponse:
    """
    Retrieve user data by username.

    Args:
        username: Username to retrieve user data for
        db: Session

    Returns:
        UserResponseSchema
    """
    cached_data = redis_client.get(username)
    if cached_data:
        return ORJSONResponse(
            content={"data": json.loads(cached_data)}, status_code=200  # noqa
        )

    user_data = UserMethods.get_record_with_(db, username=username)

    if not user_data:
        raise HTTPException(detail=NO_DATA_FOUND, status_code=status.HTTP_404_NOT_FOUND)
    user_response_schema = UserResponseSchema(
        id=user_data.id, username=user_data.username, balance=user_data.balance
    ).model_dump()

    redis_client.set(username, json.dumps(user_response_schema), ex=3600)  # noqa

    return ORJSONResponse(content={"data": user_response_schema}, status_code=200)
