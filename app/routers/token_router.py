import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy.orm import Session

from ..models.pset_models import User
from .. import dal


# to get a string like this run:
# >>> openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_LIFETIME = int(os.getenv("TOKEN_LIFETIME"))

router = APIRouter()

# -------------------------------- token 
@router.post("/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(dal.get_users_db),
) -> str:
    user = authenticated_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=TOKEN_LIFETIME)
    token = create_access_token(payload={"sub": form_data.username, "role": user.role}, 
                                expires_delta=access_token_expires)
    return token

# --------------------------- aux

def authenticated_user(db: Session, username: str, password: str):
    """ Login for token issue """
    user = db.get(User, username)
    ### на той випадок, якщо в базу вставляли юзера вручну
    if isinstance(user.hashed_password, str):
        user.hashed_password = user.hashed_password.encode('utf-8')
    ###    
    pass_is_ok = bcrypt.checkpw(password.encode('utf-8'), user.hashed_password)
    if pass_is_ok:
        return user
    return None


def create_access_token(payload: dict, expires_delta: timedelta | None = None):
    """
    Create a valid token.
    """
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
