from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class UserCreated:
    user_id: UUID
    email: str
    full_name: str
    timestamp: datetime


@dataclass(frozen=True)
class UserEmailChanged:
    user_id: UUID
    old_email: str
    new_email: str
    timestamp: datetime


@dataclass(frozen=True)
class UserPasswordChanged:
    user_id: UUID
    email: str
    timestamp: datetime
