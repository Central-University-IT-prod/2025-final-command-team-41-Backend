from typing import Protocol


class StorageRepository(Protocol):
    async def upload_file(
        self,
        content: bytes,
        content_type: str = 'application/octet-stream',
    ) -> str:
        pass
