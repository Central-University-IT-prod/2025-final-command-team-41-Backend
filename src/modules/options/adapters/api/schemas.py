from uuid import UUID

from pydantic import BaseModel, Field


class OptionCreateSchema(BaseModel):
    coworking_id: UUID
    name: str = Field(min_length=1)


class OptionResponseSchema(BaseModel):
    id: UUID
    coworking_id: UUID
    name: str

    class Config:
        from_attributes = True
