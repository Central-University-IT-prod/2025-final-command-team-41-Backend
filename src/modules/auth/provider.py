from dishka import Provider, Scope, provide  # type: ignore

from src.core.database import (
    TransactionManager,
)
from src.core.events import EventBus
from src.core.settings import Settings
from src.modules.auth.application.services import AuthService
from src.modules.auth.domain.services import (
    PasswordHasher,
    TokenService,
    YandexOIDCService,
)
from src.modules.auth.infrastructure.services.jwt_service import JWTTokenService
from src.modules.auth.infrastructure.services.yandex_oidc_service import (
    YandexOIDCService as YandexOIDCServiceImpl,
)
from src.modules.users.domain.repositories import UserRepository


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    def get_token_service(self, settings: Settings) -> TokenService:
        return JWTTokenService(settings)

    @provide(scope=Scope.APP)
    def get_yandex_oidc_service(self) -> YandexOIDCService:
        return YandexOIDCServiceImpl()

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self,
        user_repo: UserRepository,
        token_service: TokenService,
        password_hasher: PasswordHasher,
        yandex_oidc_service: YandexOIDCService,
        event_bus: EventBus,
        transaction_manager: TransactionManager,
    ) -> AuthService:
        return AuthService(
            user_repo,
            token_service,
            password_hasher,
            yandex_oidc_service,
            event_bus,
            transaction_manager,
        )
