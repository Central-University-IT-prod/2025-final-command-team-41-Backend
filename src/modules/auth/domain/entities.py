from dataclasses import dataclass
from datetime import datetime


@dataclass
class Token:
    access_token: str
    token_type: str = 'bearer'  # noqa: S105
    expires_at: datetime | None = None


@dataclass
class YandexOAuthPayload:
    token: str


@dataclass
class YandexUserData:
    email: str
    full_name: str
    phone_number: str | None = None
