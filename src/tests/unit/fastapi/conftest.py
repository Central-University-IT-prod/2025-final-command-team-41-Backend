import fastapi.testclient
import pytest

from src.entrypoints.rest.main import create_app


@pytest.fixture(scope='session')
def app() -> fastapi.FastAPI:
    return create_app()


@pytest.fixture(scope='class')
def client(app: fastapi.FastAPI) -> fastapi.testclient.TestClient:
    return fastapi.testclient.TestClient(app)
