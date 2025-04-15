import dishka

from src.modules.storage.domain.repositories import StorageRepository


class StorageService:
    def __init__(self, storage_repository: StorageRepository) -> None:
        self.storage_repository = storage_repository

    async def upload_file(
        self,
        content: bytes,
        content_type: str = 'application/octet-stream',
    ) -> str:
        return await self.storage_repository.upload_file(content, content_type)

    async def download_file(self, file_id: str) -> tuple[bytes, str]:
        return await self.storage_repository.download_file(file_id)


service_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
service_provider.provide(StorageService)
