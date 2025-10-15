import pytest

from app.app_layer.services.csv_normalization.normalizer import DataNormalizer
from app.app_layer.services.csv_normalization.service import CSVService


@pytest.fixture
def data_normalizer() -> DataNormalizer:
    return DataNormalizer()


@pytest.fixture
def csv_service(data_normalizer: DataNormalizer) -> CSVService:
    return CSVService(normalizer=data_normalizer)
