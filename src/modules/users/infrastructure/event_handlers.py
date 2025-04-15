from typing import Any

from src.core.logging import get_logger, log_extra
from src.modules.users.domain.events import (
    UserCreated,
    UserEmailChanged,
    UserPasswordChanged,
)

logger = get_logger(__name__)


class UserEventLogger:
    async def handle(self, event: Any) -> None:
        if isinstance(event, UserCreated):
            logger.info(
                'User created successfully',
                **log_extra(
                    user_id=event.user_id,
                    email=event.email,
                    full_name=event.full_name,
                    timestamp=event.timestamp.isoformat(),
                ),
            )
        elif isinstance(event, UserEmailChanged):
            logger.info(
                'User email changed',
                **log_extra(
                    user_id=event.user_id,
                    old_email=event.old_email,
                    new_email=event.new_email,
                    timestamp=event.timestamp.isoformat(),
                ),
            )
        elif isinstance(event, UserPasswordChanged):
            logger.info(
                'User password changed',
                **log_extra(
                    user_id=event.user_id,
                    email=event.email,
                    timestamp=event.timestamp.isoformat(),
                ),
            )
