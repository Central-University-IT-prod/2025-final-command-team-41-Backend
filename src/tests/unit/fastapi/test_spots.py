import datetime

import fastapi.testclient
import httpx  # noqa
import pytest


@pytest.mark.asyncio
class TestSpots:
    @pytest.fixture(autouse=True)
    def setup(self, client: fastapi.testclient.TestClient) -> None:
        self.client = client

    async def test_create_spots(self) -> None:
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

        coworking_id = response.json().get('id')

        body = [
            {
                'name': 'второй монитор',
                'description': 'широкий',
                'position': 0,
            },
            {
                'name': 'унитаз',
                'description': 'позолоченый',
                'position': 1,
            },
        ]
        response: httpx.Response = self.client.post(f'/coworkings/{coworking_id}/spots', json=body)

        assert response.status_code == fastapi.status.HTTP_200_OK

        response: httpx.Response = self.client.get(f'/coworkings/{coworking_id}/spots')

        assert response.status_code == fastapi.status.HTTP_200_OK
        assert len(response.json()) == 2
