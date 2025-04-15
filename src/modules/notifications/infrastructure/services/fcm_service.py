import http
import json
import pathlib
from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

import aiohttp

from src.core.logging import get_logger
from src.core.settings import Settings
from src.modules.notifications.domain.entities import NotificationType
from src.modules.notifications.domain.exceptions import FCMServiceError
from src.modules.notifications.domain.repositories import DeviceTokenRepository
from src.modules.notifications.domain.services import FcmNotificationService

logger = get_logger(__name__)


class FCMNotificationService(FcmNotificationService):
    FCM_URL = 'https://fcm.googleapis.com/v1/projects/{}/messages:send'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'  # noqa: S105
    SCOPE = 'https://www.googleapis.com/auth/firebase.messaging'

    def __init__(
        self,
        settings: Settings,
        device_token_repository: DeviceTokenRepository,
    ) -> None:
        self.settings = settings
        self.device_token_repository = device_token_repository
        self._access_token = None
        self._token_expiry = None
        with pathlib.Path(self.settings.firebase.credentials_file).open() as f:
            self.credentials = json.load(f)
        self.project_id = self.credentials['project_id']
        self.fcm_url = self.FCM_URL.format(self.project_id)

    async def _get_access_token(self) -> str:
        if self._access_token and self._token_expiry and datetime.now(UTC) < self._token_expiry:
            return self._access_token

        async with aiohttp.ClientSession() as session:
            jwt_token = self._create_jwt_token()
            data = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': jwt_token,
            }
            async with session.post(self.TOKEN_URL, data=data) as response:
                if response.status != http.HTTPStatus.OK:
                    msg = f'Failed to get access token: {await response.text()}'
                    raise FCMServiceError(
                        msg,
                    )

                token_data = await response.json()
                self._access_token = token_data['access_token']
                self._token_expiry = datetime.now(UTC) + timedelta(
                    seconds=token_data['expires_in'] - 60,
                )
                return self._access_token

    def _create_jwt_token(self) -> str:
        import jwt

        now = datetime.now(UTC)
        payload = {
            'iss': self.credentials['client_email'],
            'scope': self.SCOPE,
            'aud': self.TOKEN_URL,
            'iat': now,
            'exp': now + timedelta(hours=1),
        }
        return jwt.encode(payload, self.credentials['private_key'], algorithm='RS256')

    async def send_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> bool:
        try:
            device_tokens = await self.device_token_repository.get_by_user_id(user_id)

            if not device_tokens:
                logger.warning(f'No device tokens found for user {user_id}')
                return False

            access_token = await self._get_access_token()

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }

            message_data = {
                'type': str(notification_type.value),
                **({k: str(v) for k, v in data.items()} if data else {}),
            }

            success_count = 0
            for device_token in device_tokens:
                message = {
                    'message': {
                        'token': device_token.token,
                        'notification': {'title': title, 'body': body},
                        'data': message_data,
                        'android': {'priority': 'high'},
                        'apns': {'headers': {'apns-priority': '10'}},
                    },
                }

                async with (
                    aiohttp.ClientSession() as session,
                    session.post(
                        self.fcm_url,
                        json=message,
                        headers=headers,
                    ) as response,
                ):
                    response_text = await response.text()

                    if response.status == http.HTTPStatus.OK:
                        success_count += 1
                    else:
                        error_data = json.loads(response_text)
                        error_message = error_data.get('error', {}).get(
                            'message',
                            '',
                        )

                        if 'invalid-registration-token' in error_message.lower():
                            try:
                                await self.device_token_repository.delete_by_token(
                                    device_token.token,
                                )
                                logger.info(
                                    f'Removed invalid token {device_token.token}',
                                )
                            except Exception:
                                logger.exception(
                                    'Failed to remove invalid token',
                                )

        except Exception as e:
            logger.exception('Failed to send notification')
            msg = f'Failed to send notification: {e}'
            raise FCMServiceError(msg) from e

        else:
            return success_count > 0

    async def send_notification_to_multiple_users(
        self,
        user_ids: list[UUID],
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[dict[str, str]] = None,
    ) -> dict[UUID, bool]:
        results: dict[UUID, bool] = {}
        for user_id in user_ids:
            try:
                success = await self.send_notification(
                    user_id,
                    notification_type,
                    title,
                    body,
                    data,
                )
                results[user_id] = success
            except Exception:
                logger.exception(f'Failed to send notification to user {user_id}')
                results[user_id] = False
        return results
