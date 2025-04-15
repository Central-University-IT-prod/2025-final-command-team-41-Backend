from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.modules.notifications.domain.entities import NotificationType
from src.modules.notifications.domain.value_objects import DeviceType


class DeviceTypeEnum(str, Enum):
    ANDROID = 'android'
    IOS = 'ios'
    WEB = 'web'


class NotificationTypeEnum(str, Enum):
    FRIEND_REQUEST = 'friend_request'
    FRIEND_REQUEST_ACCEPTED = 'friend_request_accepted'
    FRIEND_REQUEST_REJECTED = 'friend_request_rejected'
    FRIEND_REQUEST_DELETED = 'friend_request_deleted'
    FRIENDSHIP_REMOVED = 'friendship_removed'
    SYSTEM = 'system'


class RegisterDeviceTokenSchema(BaseModel):
    token: str = Field(..., description='Firebase Cloud Messaging device token')
    device_type: DeviceTypeEnum = Field(..., description='Type of device')


class DeviceTokenResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    token: str
    device_type: DeviceTypeEnum
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator('device_type', mode='before')
    @classmethod
    def convert_device_type(cls, device_type: Any) -> DeviceTypeEnum:
        if isinstance(device_type, DeviceType):
            return DeviceTypeEnum(device_type.value)
        if isinstance(device_type, str):
            return DeviceTypeEnum(device_type)
        return device_type


class NotificationResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    type: NotificationTypeEnum
    title: str
    body: str
    data: dict[str, str]
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator('type', mode='before')
    @classmethod
    def convert_notification_type(cls, type_value: Any) -> NotificationTypeEnum:
        if isinstance(type_value, NotificationType):
            type_map = {
                NotificationType.FRIEND_REQUEST: NotificationTypeEnum.FRIEND_REQUEST,
                NotificationType.FRIEND_REQUEST_ACCEPTED: NotificationTypeEnum.FRIEND_REQUEST_ACCEPTED,
                NotificationType.FRIEND_REQUEST_REJECTED: NotificationTypeEnum.FRIEND_REQUEST_REJECTED,
                NotificationType.FRIEND_REQUEST_DELETED: NotificationTypeEnum.FRIEND_REQUEST_DELETED,
                NotificationType.FRIENDSHIP_REMOVED: NotificationTypeEnum.FRIENDSHIP_REMOVED,
                NotificationType.SYSTEM: NotificationTypeEnum.SYSTEM,
            }
            return type_map[type_value]
        return type_value


class NotificationsListResponseSchema(BaseModel):
    items: list[NotificationResponseSchema]
    total: int


class SendTestNotificationSchema(BaseModel):
    title: str = Field(
        ...,
        description='Title of the notification',
        min_length=1,
        max_length=255,
    )
    body: str = Field(..., description='Body of the notification', min_length=1)
    data: Optional[dict[str, str]] = Field(
        default=None,
        description='Additional data to be sent with the notification',
    )
