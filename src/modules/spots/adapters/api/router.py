import typing
from datetime import datetime
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Query

from src.core.exceptions import handle_exceptions
from src.modules.spots.adapters.api.schemas import SpotCreateSchema, SpotResponseSchema, SpotWithStatusSchema
from src.modules.spots.application.services import SpotService

router = APIRouter(prefix='/coworkings', tags=['spots'])


@router.get('/{coworking_id}/spots')
@inject
@handle_exceptions
async def get_spots_by_coworking_id(
    service: FromDishka[SpotService],
    coworking_id: UUID,
    time_from: typing.Annotated[
        datetime | None,
        Query(description='Start time for availability check'),
    ] = None,
    time_until: typing.Annotated[
        datetime | None,
        Query(description='End time for availability check'),
    ] = None,
) -> list[SpotWithStatusSchema]:
    """Получить споты коворкинга."""
    spots_data = await service.get_spots_with_status(
        coworking_id=coworking_id,
        time_from=time_from,
        time_until=time_until,
    )

    return [SpotWithStatusSchema.model_validate(spot) for spot in spots_data]


@router.post('/{coworking_id}/spots')
@inject
@handle_exceptions
async def create_spots(
    service: FromDishka[SpotService],
    coworking_id: UUID,
    spots: list[SpotCreateSchema],
) -> list[SpotResponseSchema]:
    """Создать споты."""
    spots_data = [spot.model_dump() for spot in spots]
    created_spots = await service.create_spots(coworking_id, spots_data)
    return [SpotResponseSchema.model_validate(spot) for spot in created_spots]
