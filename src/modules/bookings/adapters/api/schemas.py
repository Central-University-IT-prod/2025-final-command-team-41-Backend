import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from src.core.timezone_utils import to_client_timezone


class TimePeriodSchema(BaseModel):
    time_from: datetime.datetime
    time_until: datetime.datetime

    @field_validator('time_until')
    def validate_time_until(cls, value: datetime.datetime, info: FieldValidationInfo) -> datetime.datetime:
        current_datetime = to_client_timezone(datetime.datetime.now())
        time_from = info.data.get('time_from')
        if time_from is not None and (
            value < time_from or (value < current_datetime or time_from < current_datetime)
        ):
            raise ValueError
        return value


class TimePeriodResponseSchema(BaseModel):
    time_from: datetime.datetime
    time_until: datetime.datetime


class BookingCreateSchema(TimePeriodSchema):
    spot_id: UUID


class BookingRescheduleSchema(TimePeriodSchema):
    pass


class AddOptionSchema(BaseModel):
    option_id: UUID


class TimeSlotSchema(TimePeriodResponseSchema):
    pass


class AvailableTimeSlotsResponseSchema(BaseModel):
    available_slots: list[TimeSlotSchema]


class SpotResponseSchema(BaseModel):
    id: UUID
    name: str
    description: str

    class Config:
        from_attributes = True


class SpotSimpleResponseSchema(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class UserResponseSchema(BaseModel):
    id: UUID
    avatar_url: Optional[str] = None
    full_name: str
    email: str

    class Config:
        from_attributes = True


class CoworkingBookingResponseSchema(BaseModel):
    id: UUID
    name: str
    address: str
    opens_at: datetime.time
    closes_at: datetime.time
    spot: SpotResponseSchema

    class Config:
        from_attributes = True


class BookingResponseSchema(TimePeriodResponseSchema):
    id: UUID
    user_id: UUID
    status: str = Field(default='active')
    coworking: Optional[CoworkingBookingResponseSchema] = None

    class Config:
        from_attributes = True


class BookingDetailResponseSchema(TimePeriodResponseSchema):
    id: UUID
    user_id: UUID
    spot_id: UUID
    status: str
    options: list[UUID] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CurrentBookingResponseSchema(TimePeriodResponseSchema):
    id: UUID
    user: UserResponseSchema
    spot: SpotSimpleResponseSchema
    status: str
    options: list[UUID] = Field(default_factory=list)

    class Config:
        from_attributes = True


class BookingListResponseSchema(TimePeriodResponseSchema):
    id: UUID
    user: UserResponseSchema
    spot: SpotSimpleResponseSchema
    status: str
    options: list[UUID] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AlternativeSpotResponseSchema(BaseModel):
    message: str
    spot: Optional[SpotResponseSchema] = None
