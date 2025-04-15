import uuid
from collections.abc import AsyncGenerator, Sequence
from typing import (
    Any,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

import sqlalchemy.pool
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import Select

from src.core.settings import Settings, get_settings


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.postgres.url,
        poolclass=sqlalchemy.pool.NullPool,
    )


def create_async_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


class BaseModel(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


T = TypeVar('T')
M = TypeVar('M', bound=DeclarativeBase)


class AsyncSessionProtocol(Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    def add(self, instance: Any) -> None: ...

    async def refresh(self, instance: Any) -> None: ...

    async def get(
        self,
        entity: type[M],
        ident: Any,
        *,
        options: Optional[Sequence[Any]] = None,
    ) -> Optional[M]: ...

    async def execute(
        self,
        statement: Union[Select[Any], Any],
        params: Optional[dict[str, Any]] = None,
    ) -> Result[Any]: ...


class TransactionManager:
    def __init__(self, session: AsyncSessionProtocol) -> None:
        self._session = session

    async def __aenter__(self) -> 'TransactionManager':
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()

    @property
    def session(self) -> AsyncSessionProtocol:
        return self._session


AsyncSessionLocal = create_async_session_maker(create_engine(get_settings()))


async def get_db() -> AsyncGenerator[AsyncSessionProtocol, None]:
    async with AsyncSessionLocal() as session:
        yield session
