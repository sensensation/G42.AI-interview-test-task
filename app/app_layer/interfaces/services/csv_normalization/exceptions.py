class CsvNormalizationError(Exception):
    """Base error for CSV normalization issues."""


class CsvFileError(CsvNormalizationError):
    """Raised when uploaded file cannot be processed."""


class MissingColumnError(CsvNormalizationError):
    """Raised when required CSV columns are absent."""

    def __init__(self, missing: list[str] | tuple[str, ...]) -> None:
        columns = ", ".join(missing)
        super().__init__(f"Missing required column(s): {columns}")
        self.missing = tuple(missing)


class InvalidRowError(CsvNormalizationError):
    """Raised when a row contains invalid data."""

    def __init__(self, row_number: int, message: str) -> None:
        super().__init__(f"Row {row_number}: {message}")
        self.row_number = row_number
        self.message = message
