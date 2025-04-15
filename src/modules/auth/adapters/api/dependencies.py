import typing
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.exceptions import handle_exceptions
from src.modules.auth.application.services import AuthService

security = HTTPBearer()


@inject
@handle_exceptions
async def get_current_user_id(
    auth_service: FromDishka[AuthService],
    credentials: typing.Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UUID:
    return await auth_service.verify_token(credentials.credentials)
