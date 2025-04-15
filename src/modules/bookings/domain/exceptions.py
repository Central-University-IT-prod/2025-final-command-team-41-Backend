from fastapi import status

from src.core.exceptions import ErrorCode, register_domain_exception


class BookingNotFoundError(Exception):
    pass


class BookingOverlapError(Exception):
    pass


class InvalidBookingTimeError(Exception):
    pass


class SpotUnavailableError(Exception):
    pass


class BookingAccessDeniedError(Exception):
    pass


class SpotHasNoCurrentBookingError(Exception):
    """Exception raised when a spot has no current booking."""

    def __init__(self, message: str = 'No current booking found for this spot') -> None:
        self.message = message
        super().__init__(self.message)


register_domain_exception(
    BookingNotFoundError,
    ErrorCode.NOT_FOUND,
    status.HTTP_404_NOT_FOUND,
)

register_domain_exception(
    BookingOverlapError,
    ErrorCode.CONFLICT_ERROR,
    status.HTTP_409_CONFLICT,
)

register_domain_exception(
    InvalidBookingTimeError,
    ErrorCode.VALIDATION_ERROR,
    status.HTTP_400_BAD_REQUEST,
)

register_domain_exception(
    SpotUnavailableError,
    ErrorCode.CONFLICT_ERROR,
    status.HTTP_409_CONFLICT,
)

register_domain_exception(
    BookingAccessDeniedError,
    ErrorCode.FORBIDDEN,
    status.HTTP_403_FORBIDDEN,
)

register_domain_exception(
    SpotHasNoCurrentBookingError,
    ErrorCode.NOT_FOUND,
    status.HTTP_404_NOT_FOUND,
)
