from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import BaseModel


class OptionModel(BaseModel):
    __tablename__ = 'options'

    coworking_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('coworkings.id'),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
