from typing import Annotated, Union
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from src.core.exceptions import handle_exceptions
from src.modules.auth.adapters.api.dependencies import get_current_user_id
from src.modules.base.api.mappers import PaginationMapper
from src.modules.base.api.schemas import PaginationSchema
from src.modules.bookings.adapters.api.schemas import (
    AddOptionSchema,
    AvailableTimeSlotsResponseSchema,
    BookingCreateSchema,
    BookingDetailResponseSchema,
    BookingListResponseSchema,
    BookingRescheduleSchema,
    BookingResponseSchema,
    CurrentBookingResponseSchema,
    TimeSlotSchema,
)
from src.modules.bookings.application.services import BookingService
from src.modules.bookings.domain.exceptions import (
    BookingOverlapError,
    SpotUnavailableError,
)

router = APIRouter(tags=['bookings'])


@router.post('/bookings', status_code=status.HTTP_201_CREATED, response_model=BookingResponseSchema)
@inject
@handle_exceptions
async def create_booking(
    service: FromDishka[BookingService],
    booking_data: BookingCreateSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> Union[BookingResponseSchema, JSONResponse]:
    """Создать бронь спота."""
    try:
        booking_details = await service.create_booking(
            user_id=current_user_id,
            spot_id=booking_data.spot_id,
            time_from=booking_data.time_from,
            time_until=booking_data.time_until,
        )

        return BookingResponseSchema.model_validate(booking_details)

    except (BookingOverlapError, SpotUnavailableError):
        spot = await service.get_spot_info(booking_data.spot_id)
        alternative = await service.suggest_alternative_spot(
            coworking_id=spot.coworking_id,
            time_from=booking_data.time_from,
            time_until=booking_data.time_until,
            excluded_spot_id=booking_data.spot_id,
        )

        if alternative:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    'message': "Requested spot is no longer available. Here's an alternative spot.",
                    'spot': {
                        'id': str(alternative.id),
                        'name': alternative.name,
                        'description': alternative.description,
                    },
                },
            )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                'message': 'Requested spot is no longer available and no alternatives are available.',
                'spot': None,
            },
        )


@router.get('/users/me/bookings', response_model=list[BookingResponseSchema])
@inject
@handle_exceptions
async def get_user_bookings(
    service: FromDishka[BookingService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> list[BookingResponseSchema]:
    """Получить брони пользователя."""
    bookings = await service.get_user_bookings(current_user_id)
    return [BookingResponseSchema.model_validate(booking) for booking in bookings]


@router.get('/bookings/{booking_id}', response_model=CurrentBookingResponseSchema)
@inject
@handle_exceptions
async def get_booking_by_id(
    service: FromDishka[BookingService],
    booking_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> CurrentBookingResponseSchema:
    """Получить информацию о брони."""
    booking = await service.get_booking_by_id_with_permission_check(booking_id, current_user_id)
    return CurrentBookingResponseSchema.model_validate(booking)


@router.patch('/bookings/{booking_id}', response_model=BookingDetailResponseSchema)
@inject
@handle_exceptions
async def reschedule_booking(
    service: FromDishka[BookingService],
    booking_id: UUID,
    booking_data: BookingRescheduleSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> BookingDetailResponseSchema:
    """Перенести бронь."""
    booking = await service.reschedule_booking(
        booking_id=booking_id,
        user_id=current_user_id,
        time_from=booking_data.time_from,
        time_until=booking_data.time_until,
    )
    return BookingDetailResponseSchema.model_validate(booking)


@router.delete('/bookings/{booking_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
@handle_exceptions
async def cancel_booking(
    service: FromDishka[BookingService],
    booking_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    """Отменить бронь."""
    await service.cancel_booking_with_permission_check(booking_id, current_user_id)


@router.get('/bookings', response_model=list[BookingListResponseSchema])
@inject
@handle_exceptions
async def get_all_bookings(
    service: FromDishka[BookingService],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    count: Annotated[int, Query(gt=0)] = 10,
    page: Annotated[int, Query(ge=0)] = 0,
) -> list[BookingListResponseSchema]:
    """Получить все брони пользователя."""
    pagination = PaginationMapper.to_domain(PaginationSchema(count=count, page=page))
    bookings, _ = await service.get_all_bookings_paginated(current_user_id, pagination)
    return [BookingListResponseSchema.model_validate(booking) for booking in bookings]


@router.get('/spots/{spot_id}/current-booking', response_model=CurrentBookingResponseSchema)
@inject
@handle_exceptions
async def get_current_booking_for_spot(
    service: FromDishka[BookingService],
    spot_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> CurrentBookingResponseSchema:
    """Получить текущую бронь спота."""
    booking = await service.get_current_booking_for_spot(spot_id, current_user_id)
    return CurrentBookingResponseSchema.model_validate(booking)


@router.post('/bookings/{booking_id}/options', response_model=BookingDetailResponseSchema)
@inject
@handle_exceptions
async def add_option_to_booking(
    service: FromDishka[BookingService],
    booking_id: UUID,
    option_data: AddOptionSchema,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> BookingDetailResponseSchema:
    """Добавить к брони услугу."""
    booking = await service.add_option_to_booking(
        booking_id=booking_id,
        option_id=option_data.option_id,
        user_id=current_user_id,
    )
    return BookingDetailResponseSchema.model_validate(booking)


@router.get('/bookings/{booking_id}/available-times', response_model=AvailableTimeSlotsResponseSchema)
@inject
@handle_exceptions
async def get_available_time_slots(
    service: FromDishka[BookingService],
    booking_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> AvailableTimeSlotsResponseSchema:
    """Получить свободные слоты для переноса."""
    time_slots = await service.get_available_time_slots(
        booking_id=booking_id,
        user_id=current_user_id,
    )
    return AvailableTimeSlotsResponseSchema(
        available_slots=[
            TimeSlotSchema(time_from=slot['time_from'], time_until=slot['time_until']) for slot in time_slots
        ],
    )
