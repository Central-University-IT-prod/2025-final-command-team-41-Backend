from pydantic import BaseModel, EmailStr

from src.modules.auth.domain.entities import Token


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: str | None

    @classmethod
    def from_domain(cls, token: Token) -> 'TokenResponse':
        return cls(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_at=token.expires_at.isoformat() if token.expires_at else None,
        )


class YandexLoginRequest(BaseModel):
    token: str
