from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from api.responses import err_token
from schemas.entity import JWTTokens, UserLogin
from service.user import UserService, get_user_service

router = APIRouter(tags=["Аутентификация"])


@router.post(
    "/login",
    responses=err_token,
    summary="Логин пользователя",
    description="Проверяет пароль и выдает токены доступа.",
    response_description="Access и Refresh токены",
)
async def login_user(
    user_auth: Annotated[UserLogin, Body(description="Данные аутентификации")],
    user_service: UserService = Depends(get_user_service),
) -> JWTTokens:
    """Validate login and provide JWT tokens."""
    tokens = await user_service.login_user(**user_auth.model_dump())
    if tokens is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed")
    return tokens


@router.post(
    "/refresh",
    responses=err_token,
    summary="Перевыпуск токенов доступа",
    description="Проверяет Refresh токен и выдает новые токены доступа.",
    response_description="Access и Refresh токены",
)
async def refresh_tokens(user_service: UserService = Depends(get_user_service)) -> JWTTokens:
    """Refresh JWT tokens."""
    return await user_service.refresh_user()


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=err_token,
    summary="Логаут пользователя",
    description="Инвалидирует токены доступа пользовательской сессии.",
)
async def logout_user(user_service: UserService = Depends(get_user_service)) -> None:
    """Logs user out."""
    await user_service.logout_user()


@router.post(
    "/logout_others",
    responses=err_token,
    summary="Логаут пользователя на других устройствах",
    description="Инвалидирует токены доступа прочих сессий пользователя.",
    response_description="Access и Refresh токены",
)
async def logout_others(user_service: UserService = Depends(get_user_service)) -> JWTTokens:
    """Logs out user's other sessions."""
    return await user_service.logout_others()


@router.get(
    "/validate",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=err_token,
    summary="Проверка токена доступа",
    description="Валидирует Access токен.",
)
async def validate_auth(user_service: UserService = Depends(get_user_service)) -> None:
    """Validate Access token."""
    await user_service.validate_access()
