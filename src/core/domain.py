from dataclasses import dataclass
from uuid import UUID


@dataclass
class BaseDomain:
    id: UUID
