import datetime
from dataclasses import dataclass

from src.core.domain import BaseDomain


@dataclass
class Coworking(BaseDomain):
    name: str
    description: str
    address: str
    opens_at: datetime.time
    closes_at: datetime.time
    images: list[str]
