from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from src.core.exceptions import handle_exceptions
from src.modules.auth.adapters.api.dependencies import get_current_user_id
from src.modules.options.adapters.api.schemas import (
    OptionCreateSchema,
    OptionResponseSchema,
)
from src.modules.options.application.services import OptionService

router = APIRouter(prefix='/options', tags=['options'])


@router.post('', status_code=201, response_model=OptionResponseSchema)
@inject
@handle_exceptions
async def create_option(
    service: FromDishka[OptionService],
    option: OptionCreateSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> OptionResponseSchema:
    """Создать услугу."""
    created_option = await service.create_option(
        coworking_id=option.coworking_id,
        name=option.name,
        user_id=current_user_id,
    )
    return OptionResponseSchema.model_validate(created_option)


@router.delete('/{option_id}', status_code=204)
@inject
@handle_exceptions
async def delete_option(
    service: FromDishka[OptionService],
    option_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    """Удалить услуг."""
    await service.delete_option(option_id, current_user_id)


@router.get('', response_model=list[OptionResponseSchema])
@inject
@handle_exceptions
async def list_options(
    service: FromDishka[OptionService],
    coworking_id: UUID,
) -> list[OptionResponseSchema]:
    """Получить список услуг коворкинга."""
    options = await service.get_options_by_coworking(coworking_id)
    return [OptionResponseSchema.model_validate(option) for option in options]
