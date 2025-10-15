from fastapi import APIRouter

from app.api.rest.internal.v1.upload.api import router as upload_router

internal_api = APIRouter()

internal_api.include_router(upload_router, prefix="/v1/upload", tags=["CSV Upload"])
