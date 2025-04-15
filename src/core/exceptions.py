from collections.abc import Awaitable, Callable
from enum import StrEnum
from functools import wraps
from typing import Any, NoReturn, Optional, TypeVar

from fastapi import HTTPException, status


class ErrorCode(StrEnum):
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    NOT_FOUND = 'NOT_FOUND'
    DATABASE_ERROR = 'DATABASE_ERROR'
    AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'
    AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR'
    BUSINESS_LOGIC_ERROR = 'BUSINESS_LOGIC_ERROR'
    CONFLICT_ERROR = 'CONFLICT_ERROR'
    INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'
    BAD_REQUEST = 'BAD_REQUEST'
    FORBIDDEN = 'FORBIDDEN'


T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Awaitable[Any]])


_exception_handlers: dict[str, Callable[[Exception], NoReturn]] = {}


def register_exception_handler(
    exception_class_name: str,
    handler: Callable[[Exception], NoReturn],
) -> None:
    _exception_handlers[exception_class_name] = handler


def register_domain_exception(
    exception_class: type[Exception],
    error_code: ErrorCode,
    status_code: int,
    include_headers: Optional[dict[str, str]] = None,
) -> None:
    def handler(e: Exception) -> NoReturn:
        details = None
        if include_headers:
            details = {'headers': include_headers}

        raise APIHTTPException(
            status_code=status_code,
            error_code=error_code,
            message=str(e),
            details=details,
        )

    register_exception_handler(exception_class.__name__, handler)


def _init_exception_handlers() -> None:
    register_exception_handler(
        'ValidationError',
        lambda e: raise_validation_error(message=str(e)),
    )
    register_exception_handler(
        'NotFoundError',
        lambda e: raise_not_found(message=str(e)),
    )
    register_exception_handler(
        'DatabaseError',
        lambda e: raise_database_error(message=str(e)),
    )
    register_exception_handler(
        'AuthenticationError',
        lambda e: raise_authentication_error(message=str(e)),
    )
    register_exception_handler(
        'AuthorizationError',
        lambda e: raise_authorization_error(message=str(e)),
    )
    register_exception_handler(
        'BusinessLogicError',
        lambda e: raise_business_logic_error(message=str(e)),
    )

    register_exception_handler(
        'UserAlreadyExists',
        lambda e: raise_conflict_error(message=str(e)),
    )

    register_exception_handler(
        'InvalidCredentials',
        lambda e: _raise_invalid_credentials(e),
    )


def _raise_invalid_credentials(e: Exception) -> NoReturn:
    raise APIHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code=ErrorCode.AUTHENTICATION_ERROR,
        message=str(e),
        details={'headers': {'WWW-Authenticate': 'Bearer'}},
    )


def handle_exceptions(func: F) -> F:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            exception_name = e.__class__.__name__

            handler = _exception_handlers.get(exception_name)

            if handler:
                handler(e)
            else:
                raise_internal_server_error(message=str(e))

    return wrapper  # type: ignore


class AppExceptionError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class APIHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.error_code = error_code
        self.details = details or {}

        error_detail = {
            'code': error_code.value,
            'message': message,
            'details': self.details,
        }

        headers = None
        if self.details and 'headers' in self.details:
            headers = self.details.pop('headers')

        super().__init__(status_code=status_code, detail=error_detail, headers=headers)


def raise_validation_error(
    message: str,
    details: Optional[dict[str, Any]] = None,
) -> NoReturn:
    """Raise a validation error exception with HTTP status 422."""
    raise APIHTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code=ErrorCode.VALIDATION_ERROR,
        message=message,
        details=details,
    )


def raise_not_found(message: str, details: Optional[dict[str, Any]] = None) -> NoReturn:
    """Raise a not found exception with HTTP status 404."""
    raise APIHTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCode.NOT_FOUND,
        message=message,
        details=details,
    )


def raise_conflict_error(
    message: str,
    details: Optional[dict[str, Any]] = None,
) -> NoReturn:
    """Raise a conflict exception with HTTP status 409."""
    raise APIHTTPException(
        status_code=status.HTTP_409_CONFLICT,
        error_code=ErrorCode.CONFLICT_ERROR,
        message=message,
        details=details,
    )


def raise_database_error(
    message: str = 'Database error occurred',
    details: Optional[dict[str, Any]] = None,
) -> NoReturn:
    """Raise a database error exception with HTTP status 500."""
    raise APIHTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=ErrorCode.DATABASE_ERROR,
        message=message,
        details=details,
    )


def raise_authentication_error(
    message: str = 'Authentication failed',
    details: Optional[dict[str, Any]] = None,
) -> NoReturn:
    """Raise an authentication error exception with HTTP status 401."""
    raise APIHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code=ErrorCode.AUTHENTICATION_ERROR,
        message=message,
        details=details,
    )


def raise_authorization_error(
    message: str = 'Authorization failed',
    details: Optional[dict[str, Any]] = None,
) -> NoReturn:
    """Raise an authorization error exception with HTTP status 403."""
    raise APIHTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        error_code=ErrorCode.AUTHORIZATION_ERROR,
        message=message,
        details=details,
    )


def raise_business_logic_error(
    message: str,
    details: Optional[dict[str, Any]] = None,
) -> NoReturn:
    """Raise a business logic error exception with HTTP status 400."""
    raise APIHTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code=ErrorCode.BUSINESS_LOGIC_ERROR,
        message=message,
        details=details,
    )


def raise_internal_server_error(
    message: str = 'Internal server error',
    details: Optional[dict[str, Any]] = None,
) -> NoReturn:
    """Raise an internal server error exception with HTTP status 500."""
    raise APIHTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message=message,
        details=details,
    )


class ValidationError(AppExceptionError):
    def __init__(
        self,
        message: str = 'Validation error',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


class NotFoundError(AppExceptionError):
    def __init__(
        self,
        message: str = 'Resource not found',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class DatabaseError(AppExceptionError):
    def __init__(
        self,
        message: str = 'Database error occurred',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=500, details=details)


class AuthenticationError(AppExceptionError):
    def __init__(
        self,
        message: str = 'Authentication failed',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=401, details=details)


class AuthorizationError(AppExceptionError):
    def __init__(
        self,
        message: str = 'Authorization failed',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=403, details=details)


class BusinessLogicError(AppExceptionError):
    def __init__(
        self,
        message: str = 'Business logic error',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


_init_exception_handlers()
