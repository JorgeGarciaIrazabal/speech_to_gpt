import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from speech_to_gpt.api import app
from speech_to_gpt.db.db_init import get_session_maker
from speech_to_gpt.db.user_db import UserRepository, User as UrUser
from speech_to_gpt.db.errors import UserNotFoundError

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ["OPENSSL_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    email: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_rep() -> UserRepository:
    return UserRepository(get_session_maker())


def authenticate_user(email: str, password: str, ur: UserRepository) -> UrUser | bool:
    try:
        user = ur.get_by_email(email)
        if not verify_password(password, user.hashed_password):
            return False
        return user
    except UserNotFoundError:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    ur: UserRepository = Depends(get_user_rep),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    try:
        user = ur.get_by_email(token_data.username)
    except UserNotFoundError:
        raise credentials_exception
    return user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ur: UserRepository = Depends(get_user_rep),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, ur)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


class UserCreate(BaseModel):
    email: str
    password: str


@app.post("/users/", response_model=Token)
async def create_user(
    user: UserCreate,
    ur: UserRepository = Depends(get_user_rep),
) -> Token:
    hashed_password = get_password_hash(user.password)
    try:
        ur.add(user.email, hashed_password)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    except Exception:
        logging.exception("Error creating user")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maybe the username already exists",
        )
