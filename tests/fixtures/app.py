from collections.abc import AsyncIterator

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio

from app.main import app


@pytest.fixture
def asgi_app() -> FastAPI:
    return app


@pytest_asyncio.fixture
async def http_client(asgi_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with asgi_app.router.lifespan_context(asgi_app):
        transport = ASGITransport(app=asgi_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
