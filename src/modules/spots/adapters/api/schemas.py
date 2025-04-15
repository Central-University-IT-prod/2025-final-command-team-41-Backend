from uuid import UUID

from pydantic import BaseModel


class SpotResponseSchema(BaseModel):
    id: UUID
    coworking_id: UUID
    name: str
    description: str
    position: int
    status: str

    class Config:
        from_attributes = True


class SpotCreateSchema(BaseModel):
    name: str
    description: str
    position: int


class SpotWithStatusSchema(BaseModel):
    id: UUID
    coworking_id: UUID
    name: str
    description: str
    position: int
    status: str  # 'active' or 'inactive'

    class Config:
        from_attributes = True
