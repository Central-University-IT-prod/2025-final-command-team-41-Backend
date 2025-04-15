from fastapi import status

from src.core.exceptions import ErrorCode, register_domain_exception


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


register_domain_exception(
    UserAlreadyExistsError,
    ErrorCode.CONFLICT_ERROR,
    status.HTTP_409_CONFLICT,
)

register_domain_exception(
    UserNotFoundError,
    ErrorCode.NOT_FOUND,
    status.HTTP_404_NOT_FOUND,
)
