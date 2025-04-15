import typing

import fastapi
from dishka.integrations.fastapi import FromDishka, inject

from src.modules.storage.application.services import StorageService

router = fastapi.APIRouter(prefix='/storage', tags=['storage'])


@router.post('/upload')
@inject
async def upload_file(
    service: FromDishka[StorageService],
    file: fastapi.UploadFile,
) -> dict[typing.Literal['url'], str]:
    """Загрузить файл."""
    content = await file.read()
    identifier = await service.upload_file(content, content_type=file.content_type)

    return {'url': f'https://storage.yandexcloud.net/kurva/{identifier}'}
