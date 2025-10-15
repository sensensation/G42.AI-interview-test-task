from abc import ABC, abstractmethod


class AbstractDataNormalizer(ABC):
    @abstractmethod
    async def get_date_of_birth(self, dob: str | None) -> str: ...

    """Standardise a date-of-birth string to ISO ``YYYY-MM-DD``."""

    @abstractmethod
    async def get_phone(self, phone: str | None) -> str: ...

    """Convert ``phone`` into E.164 format, assuming ``default_country_code`` for local numbers."""
