from datetime import timedelta
from typing import Any, Protocol

from src.modules.auth.domain.entities import Token, YandexOAuthPayload, YandexUserData


class TokenService(Protocol):
    async def create_token(
        self,
        data: dict[str, Any],
        expires_delta: timedelta | None = None,
    ) -> Token: ...

    async def verify_token(self, token: str) -> dict[str, Any]: ...


class PasswordHasher(Protocol):
    async def hash_password(self, password: str) -> str: ...
    async def verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool: ...


class YandexOIDCService(Protocol):
    async def get_oidc_data(
        self,
        payload: YandexOAuthPayload,
    ) -> YandexUserData | None: ...
