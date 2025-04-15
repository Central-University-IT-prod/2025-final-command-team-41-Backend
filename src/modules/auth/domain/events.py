from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class UserAuthenticated:
    user_id: UUID
    timestamp: datetime


@dataclass(frozen=True)
class InvalidAuthenticationAttempt:
    email: str
    timestamp: datetime
    reason: str
