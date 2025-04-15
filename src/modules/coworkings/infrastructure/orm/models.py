import datetime
import uuid

from sqlalchemy import String, Time
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import BaseModel


class CoworkingModel(BaseModel):
    __tablename__ = 'coworkings'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)

    opens_at: Mapped[datetime.time] = mapped_column(Time(timezone=True), nullable=False)
    closes_at: Mapped[datetime.time] = mapped_column(Time(timezone=True), nullable=False)

    images: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
