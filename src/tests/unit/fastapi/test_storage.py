import fastapi.testclient
import httpx  # noqa
import pytest


@pytest.mark.asyncio
class TestStorage:
    @pytest.fixture(autouse=True)
    def setup(self, client: fastapi.testclient.TestClient) -> None:
        self.client = client

    async def test_upload_file(self) -> None:
        content = b'zdarova'
        files = {
            'file': ('example.txt', content, 'text/plain'),
        }

        response: httpx.Response = self.client.post('/storage/upload', files=files)

        assert response.status_code == fastapi.status.HTTP_200_OK
        assert response.json().get('url') is not None
