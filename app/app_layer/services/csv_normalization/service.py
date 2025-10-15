from csv import DictReader, DictWriter
from io import StringIO
from logging import getLogger

from starlette.datastructures import UploadFile

from app.app_layer.interfaces.services.csv_normalization import (
    CsvFileError,
    CsvNormalizationDTO,
    CsvNormalizationError,
    CsvSkippedRow,
    MissingColumnError,
)
from app.app_layer.interfaces.services.csv_normalization.service import AbstractCSVService
from app.app_layer.services.csv_normalization.normalizer import DataNormalizer

logger = getLogger(__name__)


class CSVService(AbstractCSVService):
    """Service responsible for normalizing contact data stored in CSV uploads."""

    def __init__(self, normalizer: DataNormalizer) -> None:
        self.normalizer = normalizer

    async def process(self, file: UploadFile) -> CsvNormalizationDTO:
        text = await self._read_payload(file)
        filename = await self._format_output_filename(file.filename)
        reader = DictReader(StringIO(text), delimiter=";")

        if reader.fieldnames is None:
            raise CsvNormalizationError("CSV header is missing")

        header_lookup = {name.strip().lower(): name for name in reader.fieldnames if name}
        missing = sorted({"id", "phone", "dob"} - set(header_lookup))
        if missing:
            raise MissingColumnError(missing)

        buffer = StringIO()
        writer = DictWriter(
            buffer,
            fieldnames=("id", "phone", "dob"),
            delimiter=";",
            lineterminator="\n",
        )
        writer.writeheader()

        processed_rows = 0
        normalized_rows = 0
        skipped_rows: list[CsvSkippedRow] = []

        for index, row in enumerate(reader, start=2):
            # Starting from 2 because of DictReader
            # consumes the header as the first line
            # and the second line is the file
            processed_rows += 1
            as_is_id = row.get(header_lookup["id"])

            if not as_is_id:
                skipped_rows.append(CsvSkippedRow(row_number=index, reason="ID value is missing"))
                continue

            try:
                normalized_phone = await self.normalizer.get_phone(
                    row.get(header_lookup["phone"]),
                )
                normalized_dob = await self.normalizer.get_date_of_birth(row.get(header_lookup["dob"]))
            except ValueError as exc:
                skipped_rows.append(CsvSkippedRow(row_number=index, reason=str(exc)))
                continue

            writer.writerow({"id": as_is_id, "phone": normalized_phone, "dob": normalized_dob})
            normalized_rows += 1

        summary = f"processed={processed_rows}, normalized={normalized_rows}, skipped={len(skipped_rows)}"
        details = None
        if skipped_rows:
            details = "; ".join(f"row {item.row_number}: {item.reason}" for item in skipped_rows) or ""

        logger.info(f"CSV normalization {summary=}, {details=}")

        return CsvNormalizationDTO(
            filename=filename,
            content=buffer.getvalue().encode("utf-8"),
            processed_rows=processed_rows,
            normalized_rows=normalized_rows,
            skipped_rows=len(skipped_rows),
            skipped=skipped_rows,
        )

    @staticmethod
    async def _read_payload(file: UploadFile) -> str:
        try:
            content = await file.read()
        except Exception as exc:  # pragma: no cover
            raise CsvFileError("Failed to read uploaded file") from exc

        if not content:
            raise CsvFileError("Uploaded file is empty")

        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CsvNormalizationError("CSV must be encoded as UTF-8") from exc

        return decoded

    @staticmethod
    async def _format_output_filename(original: str | None) -> str:
        """Return a deterministic CSV filename prefixed with ``normalized-``."""
        base = (original or "contacts.csv").strip() or "contacts.csv"
        if not base.lower().startswith("normalized-"):
            base = f"normalized-{base}"
        if not base.lower().endswith(".csv"):
            base = f"{base}.csv"
        return base
