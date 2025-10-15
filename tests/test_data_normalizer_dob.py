import csv
from pathlib import Path

import pytest

from app.app_layer.services.csv_normalization.normalizer import DataNormalizer

_RESOURCES_DIR = Path(__file__).resolve().parent / "resources"

with (_RESOURCES_DIR / "input_data.csv").open(encoding="utf-8") as source_file:
    _INPUT_ROWS = list(csv.DictReader(source_file, delimiter=";"))
with (_RESOURCES_DIR / "test.csv").open(encoding="utf-8") as expected_file:
    _EXPECTED_OUTPUT = {row["id"]: row for row in csv.DictReader(expected_file, delimiter=";")}

_DOB_CASES = [pytest.param(row["dob"], _EXPECTED_OUTPUT[row["id"]]["dob"], id=row["id"]) for row in _INPUT_ROWS]
_PHONE_CASES = [pytest.param(row["phone"], _EXPECTED_OUTPUT[row["id"]]["phone"], id=row["id"]) for row in _INPUT_ROWS]


@pytest.mark.parametrize(("raw_dob", "expected_dob"), _DOB_CASES)
async def test_get_date_of_birth_normalizes_to_iso(
    raw_dob: str,
    expected_dob: str,
    data_normalizer: DataNormalizer,
):
    normalized: str = await data_normalizer.get_date_of_birth(raw_dob)

    assert normalized == expected_dob


@pytest.mark.parametrize(("raw_phone", "expected_phone"), _PHONE_CASES)
async def test_get_phone_normalizes_to_e164(
    raw_phone: str,
    expected_phone: str,
    data_normalizer: DataNormalizer,
):
    normalized: str = await data_normalizer.get_phone(raw_phone)

    assert normalized == expected_phone
