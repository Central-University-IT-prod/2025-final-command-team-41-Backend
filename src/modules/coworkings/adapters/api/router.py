from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Query

from src.core.exceptions import handle_exceptions
from src.modules.base.api.mappers import PaginationMapper
from src.modules.base.api.schemas import PaginationSchema
from src.modules.coworkings.adapters.api.schemas import (
    CoworkingCreateSchema,
    CoworkingDetailResponseSchema,
    CoworkingListResponseSchema,
    ImageResponseSchema,
    ImageUploadSchema,
)
from src.modules.coworkings.application.services import CoworkingService

router = APIRouter(prefix='/coworkings', tags=['coworkings'])


@router.get('/')
@inject
@handle_exceptions
async def list_coworkings(
    service: FromDishka[CoworkingService],
    count: int = Query(default=10, gt=0),
    page: int = Query(default=0, ge=0),
) -> list[CoworkingListResponseSchema]:
    """Получить список коворкингов."""
    pagination = PaginationMapper.to_domain(PaginationSchema(count=count, page=page))
    coworkings = await service.list_coworkings(pagination)
    return [CoworkingListResponseSchema.model_validate(coworking) for coworking in coworkings]


@router.get('/{coworking_id}')
@inject
@handle_exceptions
async def get_coworking(
    service: FromDishka[CoworkingService],
    coworking_id: UUID,
) -> CoworkingDetailResponseSchema:
    """Получить информацию о коворкинге."""
    coworking = await service.get_coworking(coworking_id)
    return CoworkingDetailResponseSchema.model_validate(coworking)


@router.post('/')
@inject
@handle_exceptions
async def create_coworking(
    service: FromDishka[CoworkingService],
    coworking: CoworkingCreateSchema,
) -> CoworkingDetailResponseSchema:
    """Создать коворкинг."""
    created_coworking = await service.create_coworking(
        name=coworking.name,
        description=coworking.description,
        address=coworking.address,
        opens_at=coworking.opens_at,
        closes_at=coworking.closes_at,
    )
    return CoworkingDetailResponseSchema.model_validate(created_coworking)


@router.post('/{coworking_id}/images')
@inject
@handle_exceptions
async def upload_coworking_image(
    service: FromDishka[CoworkingService],
    coworking_id: UUID,
    image_data: ImageUploadSchema,
) -> ImageResponseSchema:
    """Загрузить изображение для коворкинга."""
    file_id = await service.upload_coworking_image(
        coworking_id=coworking_id,
        image_data=image_data.image,
        content_type=image_data.content_type,
    )
    return ImageResponseSchema(url=file_id)


@router.delete('/{coworking_id}/images/{image_url:path}')
@inject
@handle_exceptions
async def delete_coworking_image(
    service: FromDishka[CoworkingService],
    coworking_id: UUID,
    image_url: str,
) -> None:
    """Удалить изображение коворкинга."""
    await service.delete_coworking_image(
        coworking_id=coworking_id,
        image_url=image_url,
    )
