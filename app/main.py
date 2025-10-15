from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from inspect import isawaitable
from logging import getLogger

from fastapi import FastAPI

from app.api import rest
from app.api.rest.controllers import init_rest_api
from app.configs.base import settings
from app.containers import Container

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncIterator[None]:
    app_.state.container = Container()
    app_.state.container.wire(
        packages=[
            rest,
        ],
    )
    logger.info(f"Container resources: {app_.state.container.providers}")

    init_result = app_.state.container.init_resources()  # type: ignore[misc]
    if isawaitable(init_result):
        await init_result

    yield

    shutdown_result = app_.state.container.shutdown_resources()  # type: ignore[misc]
    if isawaitable(shutdown_result):
        await shutdown_result


def init_api_docs(app: FastAPI, *, show_docs: bool, api_root: str) -> None:
    if not show_docs:
        return

    _ = api_root
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    app.openapi_url = "/openapi.json"
    app.setup()


app = FastAPI(version=settings.api.docs_version, lifespan=lifespan)

init_api_docs(app, show_docs=settings.api.docs_enabled, api_root=settings.api.public_prefix)
init_rest_api(app)
