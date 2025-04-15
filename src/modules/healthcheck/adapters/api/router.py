from fastapi import APIRouter

from src.core.exceptions import handle_exceptions
from src.modules.healthcheck.adapters.api.schemas import HealthCheckSchema

router = APIRouter(prefix='/healthcheck', tags=['health check'])


@router.head('/')
@handle_exceptions
async def health_check() -> HealthCheckSchema:
    """мегазорд"""
    return HealthCheckSchema()
