from fastapi import status

from src.core.exceptions import ErrorCode, register_domain_exception


class OptionNotFoundError(Exception):
    pass


class NotBusinessUserError(Exception):
    pass


register_domain_exception(
    OptionNotFoundError,
    ErrorCode.NOT_FOUND,
    status.HTTP_404_NOT_FOUND,
)

register_domain_exception(
    NotBusinessUserError,
    ErrorCode.FORBIDDEN,
    status.HTTP_403_FORBIDDEN,
)
