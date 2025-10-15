from pydantic import Field
from pydantic_settings import BaseSettings

MONTH_MAP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


class DataNormalizerSettings(BaseSettings):
    default_country_code: str = Field(
        default="971",
        description="Country code appended when inputs resemble local phone numbers.",
    )
    default_year_pivot: int = Field(
        default=25,
        description="Two-digit birth years <= pivot map to 20xx, otherwise to 19xx.",
    )
    base_year: int = Field(
        default=1900,
        description="Lower bound for interpreting four-digit birth years.",
    )

    @property
    def month_map(self) -> dict[str, int]:
        return MONTH_MAP
