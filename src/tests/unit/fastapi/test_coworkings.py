import datetime
import uuid

import fastapi.testclient
import httpx  # noqa
import pytest


@pytest.mark.asyncio
class TestCoworkings:
    @pytest.fixture(autouse=True)
    def setup(self, client: fastapi.testclient.TestClient) -> None:
        self.client = client

    async def test_create_coworking(self) -> None:
        body = {
            'name': 'string',
            'description': 'string',
            'address': 'string',
            'opens_at': datetime.time(hour=8, tzinfo=datetime.UTC).isoformat(),
            'closes_at': datetime.time(hour=22, tzinfo=datetime.UTC).isoformat(),
        }
        response: httpx.Response = self.client.post('/coworkings/', json=body)

        assert response.status_code == fastapi.status.HTTP_200_OK
        assert response.json().get('id') is not None

        coworking_id = response.json()['id']

        try:
            uuid.UUID(coworking_id)

        except ValueError:
            pytest.fail('invalid uuid passed')

        response: httpx.Response = self.client.get(f'/coworkings/{coworking_id}')

        assert response.status_code == fastapi.status.HTTP_200_OK

        assert response.json().get('id') is not None
        assert response.json().get('name') is not None
        assert response.json().get('description') is not None
        assert response.json().get('address') is not None
        assert response.json().get('opens_at') is not None
        assert response.json().get('closes_at') is not None
