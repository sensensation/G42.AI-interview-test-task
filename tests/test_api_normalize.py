from collections.abc import Callable
from pathlib import Path

from httpx import AsyncClient
import pytest


async def test_normalize_endpoint_returns_csv(
    http_client: AsyncClient,
    input_csv_path: Path,
    expected_csv_path: Path,
    load_bytes: Callable[[Path], bytes],
):
    files = {"file": (input_csv_path.name, load_bytes(input_csv_path), "text/csv")}

    response = await http_client.post("/api/internal/v1/upload/normalize", files=files)

    assert response.status_code == 200
    assert response.content == load_bytes(expected_csv_path)
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == 'attachment; filename="normalized-input_data.csv"'
    assert response.headers["x-csv-processed"] == "50"
    assert response.headers["x-csv-normalized"] == "50"
    assert response.headers["x-csv-skipped"] == "0"


async def test_normalize_endpoint_requires_file(http_client: AsyncClient):
    response = await http_client.post("/api/internal/v1/upload/normalize")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail
    assert detail[0]["msg"].startswith("Field required")


async def test_normalize_endpoint_rejects_empty_file(http_client: AsyncClient):
    files: dict[str, tuple[str, bytes, str]] = {"file": ("empty.csv", b"", "text/csv")}

    response = await http_client.post("/api/internal/v1/upload/normalize", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty"


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(b"\xff\xfe\x00\x00", id="bom"),
        pytest.param("ä".encode("latin-1"), id="latin-1"),
    ],
)
async def test_normalize_endpoint_rejects_non_utf8(http_client: AsyncClient, payload: bytes):
    files: dict[str, tuple[str, bytes, str]] = {"file": ("data.csv", payload, "text/csv")}

    response = await http_client.post("/api/internal/v1/upload/normalize", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "CSV must be encoded as UTF-8"
