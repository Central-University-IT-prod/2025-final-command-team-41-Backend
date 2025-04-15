from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.core.events import EventBus
from src.core.exceptions import NotFoundError
from src.modules.auth.domain.entities import Token, YandexOAuthPayload
from src.modules.auth.domain.events import (
    InvalidAuthenticationAttempt,
    UserAuthenticated,
)
from src.modules.auth.domain.exceptions import InvalidCredentialsError
from src.modules.auth.domain.services import (
    PasswordHasher,
    TokenService,
    YandexOIDCService,
)
from src.modules.users.domain.entities import User
from src.modules.users.domain.repositories import UserRepository


@dataclass
class AuthenticateUserCommand:
    user_repo: UserRepository
    email: str
    password: str
    token_service: TokenService
    password_hasher: PasswordHasher
    event_bus: EventBus

    async def __call__(self) -> Token:
        user = await self.user_repo.get_by_email(self.email)
        if not user:
            await self.event_bus.publish(
                InvalidAuthenticationAttempt(
                    email=self.email,
                    timestamp=datetime.now(UTC),
                    reason='User not found',
                ),
            )
            msg = 'Incorrect email or password'
            raise InvalidCredentialsError(msg)

        if not await self.password_hasher.verify_password(
            self.password,
            user.hashed_password,
        ):
            await self.event_bus.publish(
                InvalidAuthenticationAttempt(
                    email=self.email,
                    timestamp=datetime.now(UTC),
                    reason='Invalid password',
                ),
            )
            msg = 'Incorrect email or password'
            raise InvalidCredentialsError(msg)

        token = await self.token_service.create_token(
            data={'sub': str(user.id)},
            expires_delta=timedelta(minutes=10080),
        )

        await self.event_bus.publish(
            UserAuthenticated(user_id=user.id, timestamp=datetime.now(UTC)),
        )

        return token


@dataclass
class AuthenticateYandexUserCommand:
    user_repo: UserRepository
    token_service: TokenService
    yandex_service: YandexOIDCService
    password_hasher: PasswordHasher
    event_bus: EventBus
    token: str

    async def __call__(self) -> Token:
        oidc_data = await self.yandex_service.get_oidc_data(
            YandexOAuthPayload(token=self.token),
        )
        if not oidc_data:
            await self.event_bus.publish(
                InvalidAuthenticationAttempt(
                    email='unknown',
                    timestamp=datetime.now(UTC),
                    reason='Invalid Yandex token',
                ),
            )
            msg = 'Invalid Yandex token'
            raise InvalidCredentialsError(msg)

        try:
            user = await self.user_repo.get_by_email(oidc_data.email)
        except NotFoundError:
            random_password = uuid4().hex
            hashed_password = await self.password_hasher.hash_password(random_password)
            user = User(
                id=uuid4(),
                email=oidc_data.email,
                full_name=oidc_data.full_name,
                hashed_password=hashed_password,
            )
            await self.user_repo.create(user)

        token = await self.token_service.create_token(
            data={'sub': str(user.id)},
            expires_delta=timedelta(minutes=10080),
        )

        await self.event_bus.publish(
            UserAuthenticated(user_id=user.id, timestamp=datetime.now(UTC)),
        )

        return token
