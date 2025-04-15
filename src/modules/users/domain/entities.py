from dataclasses import dataclass

from src.core.domain import BaseDomain


@dataclass
class User(BaseDomain):
    email: str
    full_name: str
    hashed_password: str
    is_business: bool = False
    is_banned: bool = False
    avatar_url: str | None = None

    def change_email(self, new_email: str) -> None:
        self.email = new_email

    def change_full_name(self, new_full_name: str) -> None:
        self.full_name = new_full_name
