from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from src.core.settings import Settings
from src.modules.auth.domain.entities import Token
from src.modules.auth.domain.exceptions import TokenValidationError
from src.modules.auth.domain.services import TokenService


class JWTTokenService(TokenService):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def create_token(
        self,
        data: dict[str, Any],
        expires_delta: timedelta | None = None,
    ) -> Token:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=self.settings.jwt.expire)

        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.jwt.secret,
            algorithm=self.settings.jwt.algorithm,
        )

        return Token(access_token=encoded_jwt, expires_at=expire)

    async def verify_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self.settings.jwt.secret,
                algorithms=[self.settings.jwt.algorithm],
            )
        except JWTError as e:
            msg = 'Could not validate credentials'
            raise TokenValidationError(msg) from e
