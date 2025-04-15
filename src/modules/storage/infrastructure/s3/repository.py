import mimetypes
import uuid

import aioboto3

from src.modules.storage.domain.repositories import (
    StorageRepository,
)


class S3StorageRepository(StorageRepository):
    def __init__(
        self,
        access_key_id: str,
        access_key: str,
        bucket: str,
    ) -> None:
        self.endpoint = 'https://storage.yandexcloud.net'
        self.access_key_id = access_key_id
        self.access_key = access_key
        self.bucket = bucket

    async def upload_file(
        self,
        content: bytes,
        content_type: str = 'application/octet-stream',
    ) -> str:
        session = aioboto3.Session()
        key = str(uuid.uuid4())

        async with session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.access_key,
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content,
                ContentType=content_type,
            )

        return key


def get_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'
