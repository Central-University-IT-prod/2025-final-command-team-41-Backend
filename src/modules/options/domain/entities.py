from dataclasses import dataclass
from uuid import UUID

from src.core.domain import BaseDomain


@dataclass
class Option(BaseDomain):
    coworking_id: UUID
    name: str
