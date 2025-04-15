from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from src.core.exceptions import APIHTTPException, AppExceptionError, ErrorCode


def setup_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIHTTPException)
    async def api_http_exception_handler(  # type: ignore
        request: Request,
        exc: APIHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={'error': exc.detail},
        )

    @app.exception_handler(AppExceptionError)
    async def app_exception_handler(  # type: ignore
        request: Request,
        exc: AppExceptionError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'error': {
                    'type': exc.__class__.__name__,
                    'message': exc.message,
                    'details': exc.details,
                },
            },
        )

    @app.exception_handler(PydanticValidationError)
    async def validation_exception_handler(  # type: ignore
        request: Request,
        exc: PydanticValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                'error': {
                    'code': ErrorCode.VALIDATION_ERROR.value,
                    'message': 'Validation error',
                    'details': {'errors': exc.errors()},
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(  # type: ignore
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                'error': {
                    'code': ErrorCode.INTERNAL_SERVER_ERROR.value,
                    'message': 'An unexpected error occurred',
                    'details': {'error': str(exc)},
                },
            },
        )
