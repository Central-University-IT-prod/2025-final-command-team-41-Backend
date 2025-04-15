import datetime
import typing
from uuid import UUID

import pydantic
from pydantic import BaseModel, Field


class CoworkingListResponseSchema(BaseModel):
    id: UUID
    name: str
    address: str
    opens_at: datetime.time
    closes_at: datetime.time

    class Config:
        from_attributes = True


class CoworkingDetailResponseSchema(BaseModel):
    id: UUID
    name: str
    description: str
    address: str
    opens_at: datetime.time
    closes_at: datetime.time
    images: list[str]

    class Config:
        from_attributes = True


class CoworkingCreateSchema(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    address: str = Field(min_length=1)
    opens_at: datetime.time
    closes_at: datetime.time

    @pydantic.model_validator(mode='after')
    def validate_time_fields_have_utcoffset(self) -> typing.Any:
        if self.opens_at.utcoffset() is None:
            msg = 'opens_at must have a UTC offset'
            raise ValueError(msg)

        if self.closes_at.utcoffset() is None:
            msg = 'closes_at must have a UTC offset'
            raise ValueError(msg)

        return self


class ImageUploadSchema(BaseModel):
    image: str
    content_type: str = 'image/jpeg'


class ImageResponseSchema(BaseModel):
    url: str
