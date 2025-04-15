from typing import Annotated
from uuid import UUID

import fastapi
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from src.core.exceptions import (
    handle_exceptions,
)
from src.modules.auth.adapters.api.dependencies import get_current_user_id
from src.modules.users.adapters.api.schemas import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)
from src.modules.users.application.services import UserService

router = APIRouter(prefix='/users', tags=['users'])


@router.post('', status_code=201)
@inject
@handle_exceptions
async def create_user(
    service: FromDishka[UserService],
    user: UserCreateSchema,
) -> None:
    """Создать пользователя."""
    await service.create_user(
        email=user.email,
        full_name=user.full_name,
        password=user.password,
        is_business=user.is_business,
        avatar_url=str(user.avatar_url) if user.avatar_url is not None else None,
    )


@router.get('/me')
@inject
@handle_exceptions
async def get_user_me(
    service: FromDishka[UserService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> UserResponseSchema:
    """Получить профиль пользователя."""
    user = await service.get_user(current_user_id)
    return UserResponseSchema.model_validate(user)


@router.post('/{user_id}/ban', status_code=fastapi.status.HTTP_204_NO_CONTENT)
@inject
@handle_exceptions
async def ban_user(
    service: FromDishka[UserService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_id: UUID,
) -> None:
    """Добавить пользователя в черный список."""
    callee = await service.get_user(current_user_id)

    if not callee.is_business:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail='Non-business account callee.',
        )

    await service.ban_user(user_id)


@router.post('/{user_id}/unban', status_code=fastapi.status.HTTP_204_NO_CONTENT)
@inject
@handle_exceptions
async def unban_user(
    service: FromDishka[UserService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_id: UUID,
) -> None:
    """Удалить пользователя из черного списка."""
    callee = await service.get_user(current_user_id)

    if not callee.is_business:
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail='Non-business account callee.',
        )

    await service.unban_user(user_id)


@router.get('/{user_id}')
@inject
@handle_exceptions
async def get_user(
    service: FromDishka[UserService],
    user_id: UUID,
) -> UserResponseSchema:
    """Получить информацию о пользователе."""
    user = await service.get_user(user_id)
    return UserResponseSchema.model_validate(user)


@router.patch('/{user_id}')
@inject
@handle_exceptions
async def update_user(
    service: FromDishka[UserService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_id: UUID,
    user_data: UserUpdateSchema,
) -> UserResponseSchema:
    """Обновить данные пользователя..."""
    updated_user = await service.update_user(
        user_id=user_id,
        current_user_id=current_user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        avatar_url=str(user_data.avatar_url) if user_data.avatar_url is not None else None,
    )
    return UserResponseSchema.model_validate(updated_user)
