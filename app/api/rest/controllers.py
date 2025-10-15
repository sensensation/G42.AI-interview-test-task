from fastapi import FastAPI

from app.api.rest.internal.controllers import internal_api


def init_rest_api(app: FastAPI) -> FastAPI:
    app.include_router(internal_api, prefix="/api/internal")
