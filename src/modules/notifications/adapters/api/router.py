from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query, status

from src.core.exceptions import handle_exceptions
from src.modules.auth.adapters.api.dependencies import get_current_user_id
from src.modules.base.api.mappers import PaginationMapper
from src.modules.base.api.schemas import PaginationSchema
from src.modules.notifications.adapters.api.schemas import (
    DeviceTokenResponseSchema,
    NotificationResponseSchema,
    NotificationsListResponseSchema,
    RegisterDeviceTokenSchema,
    SendTestNotificationSchema,
)
from src.modules.notifications.application.services import NotificationsService
from src.modules.notifications.domain.entities import NotificationType

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.post('/device-tokens', status_code=status.HTTP_201_CREATED)
@inject
@handle_exceptions
async def register_device_token(
    service: FromDishka[NotificationsService],
    token_data: RegisterDeviceTokenSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> DeviceTokenResponseSchema:
    """Зарегистрировать токен девайса."""
    device_token = await service.register_device_token(
        user_id=current_user_id,
        token=token_data.token,
        device_type=token_data.device_type.value,
    )
    return DeviceTokenResponseSchema.model_validate(device_token)


@router.delete('/device-tokens/{token}')
@inject
@handle_exceptions
async def remove_device_token(
    service: FromDishka[NotificationsService],
    token: str,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    """Удалить токен девайса."""
    await service.remove_device_token(token=token)


@router.get('/device-tokens')
@inject
@handle_exceptions
async def get_device_tokens(
    service: FromDishka[NotificationsService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> list[DeviceTokenResponseSchema]:
    """Получить токены девайса."""
    device_tokens = await service.get_device_tokens(user_id=current_user_id)
    return [DeviceTokenResponseSchema.model_validate(token) for token in device_tokens]


@router.get('')
@inject
@handle_exceptions
async def get_notifications(
    service: FromDishka[NotificationsService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    pagination: Annotated[PaginationSchema, Query(...)],
) -> NotificationsListResponseSchema:
    """Получить уведомления."""
    notifications = await service.get_notifications(
        current_user_id,
        PaginationMapper.to_domain(pagination),
    )
    return NotificationsListResponseSchema(
        items=[NotificationResponseSchema.model_validate(n, from_attributes=True) for n in notifications],
        total=len(notifications),
    )


@router.get('/{notification_id}')
@inject
@handle_exceptions
async def get_notification(
    service: FromDishka[NotificationsService],
    notification_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> NotificationResponseSchema:
    """Получить уведомление."""
    notification = await service.get_notification(notification_id=notification_id)
    return NotificationResponseSchema.model_validate(notification)


@router.post('/{notification_id}/read')
@inject
@handle_exceptions
async def mark_notification_as_read(
    service: FromDishka[NotificationsService],
    notification_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    """Пометить уведомление как прочитанное."""
    await service.mark_notification_as_read(notification_id=notification_id)


@router.post('/read-all')
@inject
@handle_exceptions
async def mark_all_notifications_as_read(
    service: FromDishka[NotificationsService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    """Пометить все уведомления как прочитанные."""
    await service.mark_all_notifications_as_read(user_id=current_user_id)


@router.post('/test', status_code=status.HTTP_200_OK)
@inject
@handle_exceptions
async def send_test_notification(
    service: FromDishka[NotificationsService],
    notification_data: SendTestNotificationSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    """Отправить тестовое уведомление."""
    await service.send_notification(
        user_id=current_user_id,
        notification_type=NotificationType.SYSTEM,
        title=notification_data.title,
        body=notification_data.body,
        data=notification_data.data,
    )
