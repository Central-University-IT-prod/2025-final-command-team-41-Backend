from pydantic import BaseModel, Field


class PaginationSchema(BaseModel):
    count: int = Field(default=10, gt=0)
    page: int = Field(default=0, ge=0)
