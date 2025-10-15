from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette.responses import Response

from app.app_layer.services.csv_normalization import CsvNormalizationError, CSVService
from app.containers import Container

router = APIRouter()


@router.post(
    "/normalize",
    summary="Normalize uploaded CSV data",
    response_description="CSV file where phone numbers are formatted as E.164 and dates as YYYY-MM-DD",
)
@inject
async def normalize_csv(
    file: Annotated[UploadFile, File(description="CSV file with columns id;phone;dob")],
    service: Annotated[CSVService, Depends(Provide[Container.get_csv_normalization_service])],
) -> Response:
    try:
        result = await service.process(file)
    except CsvNormalizationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    headers = {
        "Content-Disposition": f'attachment; filename="{result.filename}"',
        "X-CSV-Processed": str(result.processed_rows),
        "X-CSV-Normalized": str(result.normalized_rows),
        "X-CSV-Skipped": str(result.skipped_rows),
    }

    return Response(content=result.content, media_type=result.content_type, headers=headers)
