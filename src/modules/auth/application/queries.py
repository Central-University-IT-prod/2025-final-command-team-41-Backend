from dataclasses import dataclass
from uuid import UUID

from src.modules.auth.domain.exceptions import TokenValidationError
from src.modules.auth.domain.services import TokenService


@dataclass
class VerifyTokenQuery:
    token_service: TokenService
    token: str

    async def __call__(self) -> UUID:
        payload = await self.token_service.verify_token(self.token)
        user_id = payload.get('sub')
        if user_id is None:
            msg = 'Token is missing user ID'
            raise TokenValidationError(msg)
        return UUID(user_id)
