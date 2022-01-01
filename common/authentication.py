from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JOSEError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session


from config.config import settings
from database.db import get_db
from models import User
from models.user import UserMethods

security = HTTPBearer()
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify Password.

    Args:
        plain_password: str
        hashed_password: str

    Returns:
        bool
    """
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: str

    Returns:
        Hashed Password
    """
    return PWD_CONTEXT.hash(password)


async def authenticate_user(username: str, password: str, db: Session) -> User:
    """
    Authenticate User.

    Args:
        username: str
        password: str
        db: Session

    Returns:
        User
    """
    user = UserMethods.get_record_with_(db, username=username)
    if user and verify_password(password, user.password):
        return user


def create_access_token(data: dict) -> str:
    """
    Create new Access Token

    Args:
        data: Dict

    Returns:
        str
    """
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        payload=data,
    )


def _create_token(
    token_type: str,
    lifetime: timedelta,
    payload: dict,
) -> str:
    """
    Create jwt token.

    Args:
        token_type: access_token
        lifetime: timedelta
        payload: Dict

    Returns:
        JWT Token
    """
    expire = datetime.utcnow() + lifetime
    payload["type"] = token_type
    payload["exp"] = expire
    payload["iat"] = datetime.utcnow()
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current logged-in user .

    Args:
        credentials: HTTPAuthorizationCredentials
        db: Session

    Returns:
        User
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        username: str = payload.get("username")
    except JOSEError:
        raise credentials_exception
    user = UserMethods.get_record_with_(db, username=username)
    if not user:
        raise credentials_exception
    return user
