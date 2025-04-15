from fastapi import status

from src.core.exceptions import ErrorCode, register_domain_exception


class DeviceTokenAlreadyExistsError(Exception):
    pass


class DeviceTokenNotFoundError(Exception):
    pass


class NotificationNotFoundError(Exception):
    pass


class FCMServiceError(Exception):
    pass


register_domain_exception(
    DeviceTokenAlreadyExistsError,
    ErrorCode.CONFLICT_ERROR,
    status.HTTP_409_CONFLICT,
)

register_domain_exception(
    DeviceTokenNotFoundError,
    ErrorCode.NOT_FOUND,
    status.HTTP_404_NOT_FOUND,
)

register_domain_exception(
    NotificationNotFoundError,
    ErrorCode.NOT_FOUND,
    status.HTTP_404_NOT_FOUND,
)

register_domain_exception(
    FCMServiceError,
    ErrorCode.INTERNAL_SERVER_ERROR,
    status.HTTP_500_INTERNAL_SERVER_ERROR,
)
