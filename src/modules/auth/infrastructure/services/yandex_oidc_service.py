import http

import aiohttp

from src.modules.auth.domain.entities import YandexOAuthPayload, YandexUserData


class YandexOIDCService:
    oidc_url = 'https://login.yandex.ru/info'

    async def get_oidc_data(self, payload: YandexOAuthPayload) -> YandexUserData | None:
        headers = {'Authorization': f'Bearer {payload.token}'}

        async with (
            aiohttp.ClientSession() as session,
            session.get(self.oidc_url, headers=headers) as response,
        ):
            if response.status != http.HTTPStatus.OK:
                return None
            data = await response.json()
            return YandexUserData(
                email=data.get('default_email'),
                full_name=data.get('real_name'),
                phone_number=data.get('default_phone', {}).get('number'),
            )
