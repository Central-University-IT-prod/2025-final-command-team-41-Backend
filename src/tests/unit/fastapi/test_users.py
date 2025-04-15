import fastapi.testclient
import httpx  # noqa
import pytest

from src.entrypoints.mock.main import faker


@pytest.mark.asyncio
class TestUsers:
    @pytest.fixture(autouse=True)
    def setup(self, client: fastapi.testclient.TestClient) -> None:
        self.client = client

    async def test_create_user(self) -> None:
        email = faker.email()
        body = {
            'email': email,
            'full_name': 'string',
            'password': 'string',
            'is_business': True,
            'avatar_url': 'https://example.com/',
        }
        response: httpx.Response = self.client.post('/users', json=body)

        assert response.status_code == fastapi.status.HTTP_201_CREATED

        body = {
            'email': email,
            'password': 'string',
        }
        response: httpx.Response = self.client.post('/auth/login', json=body)

        assert response.status_code == fastapi.status.HTTP_200_OK

        assert response.json().get('access_token') is not None
        assert response.json().get('token_type') is not None
        assert response.json().get('expires_at') is not None

        access_token = response.json().get('access_token')

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response: httpx.Response = self.client.get('/users/me', headers=headers)

        assert response.status_code == fastapi.status.HTTP_200_OK

        assert response.json().get('id') is not None
        assert response.json().get('email') is not None
        assert response.json().get('full_name') is not None
        assert response.json().get('is_business') is not None
        assert response.json().get('is_banned') is False

        user_id = response.json().get('id')

        response: httpx.Response = self.client.get(f'/users/{user_id}')

        assert response.status_code == fastapi.status.HTTP_200_OK

        assert response.json().get('id') is not None
        assert response.json().get('email') is not None
        assert response.json().get('full_name') is not None
        assert response.json().get('is_business') is not None
        assert response.json().get('is_banned') is False
