import base64
import datetime
from dataclasses import dataclass
from uuid import UUID, uuid4

from src.modules.coworkings.domain.entities import Coworking
from src.modules.coworkings.domain.repositories import CoworkingRepository
from src.modules.storage.application.services import StorageService


@dataclass
class CreateCoworkingCommand:
    repo: CoworkingRepository
    name: str
    description: str
    address: str
    opens_at: datetime.time
    closes_at: datetime.time
    images: list[str]

    async def __call__(self) -> Coworking:
        coworking = Coworking(
            id=uuid4(),
            name=self.name,
            description=self.description,
            address=self.address,
            opens_at=self.opens_at,
            closes_at=self.closes_at,
            images=self.images,
        )
        return await self.repo.create(coworking)


@dataclass
class UploadCoworkingImageCommand:
    repo: CoworkingRepository
    storage_service: StorageService
    coworking_id: UUID
    image_data: str
    content_type: str

    async def __call__(self) -> tuple[Coworking, str]:
        coworking = await self.repo.get_by_id(self.coworking_id)

        image_bytes = base64.b64decode(self.image_data)

        file_id = await self.storage_service.upload_file(image_bytes, self.content_type)

        coworking.images.append(file_id)

        updated_coworking = await self.repo.update(coworking)

        return updated_coworking, file_id


@dataclass
class DeleteCoworkingImageCommand:
    repo: CoworkingRepository
    coworking_id: UUID
    image_url: str

    async def __call__(self) -> Coworking:
        coworking = await self.repo.get_by_id(self.coworking_id)

        if self.image_url in coworking.images:
            coworking.images.remove(self.image_url)

        return await self.repo.update(coworking)
