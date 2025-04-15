from typing import Any

from src.core.logging import get_logger, log_extra
from src.modules.auth.domain.events import (
    InvalidAuthenticationAttempt,
    UserAuthenticated,
)

logger = get_logger(__name__)


class AuthEventLogger:
    async def handle(self, event: Any) -> None:
        if isinstance(event, UserAuthenticated):
            logger.info(
                'User authenticated successfully',
                **log_extra(
                    user_id=event.user_id,
                    timestamp=event.timestamp.isoformat(),
                ),
            )
        elif isinstance(event, InvalidAuthenticationAttempt):
            logger.warning(
                'Authentication attempt failed',
                **log_extra(
                    email=event.email,
                    reason=event.reason,
                    timestamp=event.timestamp.isoformat(),
                ),
            )
