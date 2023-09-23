from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.crud.user import get_user_by_email
from app.models.user import User
from app.schemas.user import UserAuth, UserOut

router = APIRouter()


async def authentication_user(user_auth: UserAuth):
    """
    valid check user

    return User or False
    """
    user = await get_user_by_email(user_auth.email)
    if user is None:
        return False
    if not verify_password(user_auth.password, user.password):
        return False
    return user


@router.post("/signup", response_model=UserOut)
async def create_user(user_auth: UserAuth):
    """create a new user"""
    user = await get_user_by_email(user_auth.email)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that email already exists")

    # TODO
    # email validation

    hashed_pwd = get_password_hash(user_auth.password)
    user = User(email=user_auth.email, password=hashed_pwd)
    await user.create()
    return user


@router.post("/login")
async def login(user_auth: UserAuth):
    user = await authentication_user(user_auth)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expire)

    refresh_token_expire = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expire)

    header = {"Authorization": f"Bearer {access_token}"}
    # TODO
    # content 수정
    response = JSONResponse(content={"status": "success"}, headers=header)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return response