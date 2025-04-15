from fastapi import status

from src.core.exceptions import ErrorCode, register_domain_exception


class InvalidCredentialsError(Exception):
    pass


class TokenValidationError(Exception):
    pass


register_domain_exception(
    InvalidCredentialsError,
    ErrorCode.AUTHENTICATION_ERROR,
    status.HTTP_401_UNAUTHORIZED,
    include_headers={'WWW-Authenticate': 'Bearer'},
)

register_domain_exception(
    TokenValidationError,
    ErrorCode.AUTHENTICATION_ERROR,
    status.HTTP_401_UNAUTHORIZED,
    include_headers={'WWW-Authenticate': 'Bearer'},
)
