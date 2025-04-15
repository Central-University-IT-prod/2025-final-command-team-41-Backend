from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field, field_validator

from src.core.exceptions import ValidationError


class UserCreateSchema(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1)
    password: str = Field(min_length=6)
    is_business: bool = False
    avatar_url: AnyHttpUrl | None = None

    @field_validator('full_name')
    def full_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            msg = 'Full name cannot be empty'
            raise ValidationError(msg)
        return v


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1)
    avatar_url: AnyHttpUrl | None = None

    @field_validator('full_name')
    def full_name_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            msg = 'Full name cannot be empty'
            raise ValidationError(msg)
        return v


class UserResponseSchema(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_business: bool
    is_banned: bool
    avatar_url: AnyHttpUrl | None = None

    class Config:
        from_attributes = True
