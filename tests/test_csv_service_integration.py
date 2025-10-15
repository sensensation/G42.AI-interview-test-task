from collections.abc import Callable
from pathlib import Path
from tempfile import SpooledTemporaryFile

from starlette.datastructures import UploadFile

from app.app_layer.services.csv_normalization.service import CSVService


async def test_csv_service_processes_file(
    csv_service: CSVService,
    input_csv_path: Path,
    expected_csv_path: Path,
    load_bytes: Callable[[Path], bytes],
):
    payload: bytes = load_bytes(input_csv_path)
    with SpooledTemporaryFile() as buffer:
        buffer.write(payload)
        buffer.seek(0)
        upload: UploadFile = UploadFile(filename=input_csv_path.name, file=buffer)

        try:
            result = await csv_service.process(upload)
        finally:
            await upload.close()

    assert result.filename == "normalized-input_data.csv"
    assert result.processed_rows == 50
    assert result.normalized_rows == 50
    assert result.skipped_rows == 0
    assert not result.skipped
    assert result.content_type == "text/csv"
    assert result.content == load_bytes(expected_csv_path)
