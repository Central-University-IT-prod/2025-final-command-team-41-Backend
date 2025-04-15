from dataclasses import dataclass
from uuid import UUID

from src.core.domain import BaseDomain


@dataclass
class Spot(BaseDomain):
    coworking_id: UUID
    name: str
    description: str
    position: int
    status: str = 'active'
