from abc import ABC, abstractmethod

from starlette.datastructures import UploadFile

from app.app_layer.interfaces.services.csv_normalization.dto import CsvNormalizationDTO


class AbstractCSVService(ABC):
    @abstractmethod
    async def process(self, file: UploadFile) -> CsvNormalizationDTO: ...
