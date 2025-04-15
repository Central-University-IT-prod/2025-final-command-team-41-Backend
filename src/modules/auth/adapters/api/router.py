from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.core.exceptions import (
    handle_exceptions,
)
from src.modules.auth.adapters.api.schemas import (
    LoginRequest,
    TokenResponse,
    YandexLoginRequest,
)
from src.modules.auth.application.services import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login')
@inject
@handle_exceptions
async def login(
    auth_service: FromDishka[AuthService],
    login_data: LoginRequest,
) -> TokenResponse:
    """Получить JWT токен."""
    token = await auth_service.authenticate_user(
        email=login_data.email,
        password=login_data.password,
    )
    return TokenResponse.from_domain(token)


@router.post('/login/yandex')
@inject
@handle_exceptions
async def login_yandex(
    auth_service: FromDishka[AuthService],
    login_data: YandexLoginRequest,
) -> TokenResponse:
    """Получить JWT токен через OAuth Yandex."""
    token = await auth_service.authenticate_yandex_user(token=login_data.token)
    return TokenResponse.from_domain(token)
