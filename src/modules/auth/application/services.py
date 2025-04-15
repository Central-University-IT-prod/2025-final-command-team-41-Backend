from uuid import UUID

from src.core.database import TransactionManager
from src.core.events import EventBus
from src.modules.auth.application.commands import (
    AuthenticateUserCommand,
    AuthenticateYandexUserCommand,
)
from src.modules.auth.application.queries import VerifyTokenQuery
from src.modules.auth.domain.entities import Token
from src.modules.auth.domain.services import (
    PasswordHasher,
    TokenService,
    YandexOIDCService,
)
from src.modules.users.domain.repositories import UserRepository


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_service: TokenService,
        password_hasher: PasswordHasher,
        yandex_service: YandexOIDCService,
        event_bus: EventBus,
        transaction_manager: TransactionManager,
    ) -> None:
        self.user_repo = user_repo
        self.token_service = token_service
        self.password_hasher = password_hasher
        self.yandex_service = yandex_service
        self.event_bus = event_bus
        self.transaction_manager = transaction_manager

    async def authenticate_user(self, email: str, password: str) -> Token:
        async with self.transaction_manager:
            command = AuthenticateUserCommand(
                user_repo=self.user_repo,
                email=email,
                password=password,
                token_service=self.token_service,
                password_hasher=self.password_hasher,
                event_bus=self.event_bus,
            )
            return await command()

    async def authenticate_yandex_user(self, token: str) -> Token:
        async with self.transaction_manager:
            command = AuthenticateYandexUserCommand(
                user_repo=self.user_repo,
                token_service=self.token_service,
                yandex_service=self.yandex_service,
                password_hasher=self.password_hasher,
                event_bus=self.event_bus,
                token=token,
            )
            return await command()

    async def verify_token(self, token: str) -> UUID:
        query = VerifyTokenQuery(
            token_service=self.token_service,
            token=token,
        )
        return await query()
