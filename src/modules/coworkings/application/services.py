import datetime
from typing import Optional
from uuid import UUID

from src.core.database import TransactionManager
from src.modules.base.domain.value_objects import Pagination
from src.modules.coworkings.application.commands import (
    CreateCoworkingCommand,
    DeleteCoworkingImageCommand,
    UploadCoworkingImageCommand,
)
from src.modules.coworkings.application.queries import GetCoworkingByIdQuery, ListCoworkingsQuery
from src.modules.coworkings.domain.entities import Coworking
from src.modules.coworkings.domain.repositories import CoworkingRepository
from src.modules.storage.application.services import StorageService


class CoworkingService:
    def __init__(
        self,
        repo: CoworkingRepository,
        transaction_manager: TransactionManager,
        storage_service: StorageService,
    ) -> None:
        self.repo = repo
        self.transaction_manager = transaction_manager
        self.storage_service = storage_service

    async def create_coworking(
        self,
        name: str,
        description: str,
        address: str,
        opens_at: datetime.time,
        closes_at: datetime.time,
        images: Optional[list[str]] = None,
    ) -> Coworking:
        async with self.transaction_manager:
            command = CreateCoworkingCommand(
                repo=self.repo,
                name=name,
                description=description,
                address=address,
                opens_at=opens_at,
                closes_at=closes_at,
                images=images or [],
            )
            return await command()

    async def get_coworking(self, coworking_id: UUID) -> Coworking:
        query = GetCoworkingByIdQuery(repo=self.repo)
        return await query(coworking_id)

    async def list_coworkings(self, pagination: Pagination) -> list[Coworking]:
        query = ListCoworkingsQuery(repo=self.repo)
        return await query(pagination)

    async def upload_coworking_image(
        self,
        coworking_id: UUID,
        image_data: str,
        content_type: str,
    ) -> str:
        async with self.transaction_manager:
            command = UploadCoworkingImageCommand(
                repo=self.repo,
                storage_service=self.storage_service,
                coworking_id=coworking_id,
                image_data=image_data,
                content_type=content_type,
            )
            _, file_id = await command()
            return file_id

    async def delete_coworking_image(
        self,
        coworking_id: UUID,
        image_url: str,
    ) -> None:
        async with self.transaction_manager:
            command = DeleteCoworkingImageCommand(
                repo=self.repo,
                coworking_id=coworking_id,
                image_url=image_url,
            )
            await command()
