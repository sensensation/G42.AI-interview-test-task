from calendar import monthrange
from re import IGNORECASE, findall, split, sub

from app.app_layer.interfaces.services.csv_normalization.normalizer import AbstractDataNormalizer
from app.configs.base import settings


class DataNormalizer(AbstractDataNormalizer):
    """Normalize phone numbers and birth dates."""

    def __init__(
        self,
        *,
        default_country_code: str | None = None,
        pivot_year: int | None = None,
    ):
        self.default_country_code = default_country_code or settings.normalizer.default_country_code
        self.pivot_year = pivot_year or settings.normalizer.default_year_pivot
        self.phone_translation = str.maketrans({"o": "0", "O": "0"})
        self.month_map = settings.normalizer.month_map
        self.non_digit_pattern = r"\D"
        self.digit_group_pattern = r"\d+"
        self.token_split_pattern = r"[\s,._/:;-]+"  # noqa: S105
        self.ordinal_suffix_pattern = r"(?<=\d)(st|nd|rd|th)\b"

    async def get_date_of_birth(self, dob: str | None) -> str:
        raw = "" if dob is None else str(dob).strip()
        if not raw:
            raise ValueError("Missing date of birth value")

        has_alpha = any(char.isalpha() for char in raw)
        if has_alpha:
            year, month, day = self._parse_with_month_names(raw)
        else:
            year, month, day = self._parse_numeric_date(raw)

        year, month, day = self._validate_or_swap(year, month, day)
        return f"{year:04d}-{month:02d}-{day:02d}"

    async def get_phone(self, phone: str | None) -> str:
        raw = "" if phone is None else str(phone).strip()
        if not raw:
            raise ValueError("Missing phone value")

        normalized_input = raw.translate(self.phone_translation)
        digits_only = sub(self.non_digit_pattern, "", normalized_input)
        if not digits_only:
            raise ValueError("Input phone value must contain digits")

        if raw.startswith("+"):
            normalized = digits_only
        elif digits_only.startswith("00"):
            normalized = digits_only[2:]
        elif digits_only.startswith(self.default_country_code):
            normalized = digits_only
        elif digits_only.startswith("0"):
            normalized = self.default_country_code + digits_only[1:]
        elif len(digits_only) in (9, 10):
            normalized = self.default_country_code + digits_only
        else:
            normalized = digits_only

        if len(normalized) < 6:
            raise ValueError("Phone value is too short for E.164 format")

        return f"+{normalized}"

    def _parse_numeric_date(self, raw: str) -> tuple[int, int, int]:
        parts = findall(self.digit_group_pattern, raw)
        digits_only = sub(self.non_digit_pattern, "", raw)

        if len(parts) == 3:
            first, second, third = map(int, parts)
            if first >= 1000:
                year, month, day = first, second, third
            else:
                day, month, year = first, second, third
                if month > 12 and day <= 12:
                    day, month = month, day
            year = self._expand_year(year)
        elif len(parts) == 1 and len(digits_only) in (6, 8):
            if len(digits_only) == 8:
                leading = int(digits_only[:4])
                if leading >= settings.normalizer.base_year:
                    year = leading
                    month = int(digits_only[4:6])
                    day = int(digits_only[6:8])
                else:
                    day = int(digits_only[:2])
                    month = int(digits_only[2:4])
                    year = int(digits_only[4:8])
            else:
                day = int(digits_only[:2])
                month = int(digits_only[2:4])
                year = int(digits_only[4:6])
            year = self._expand_year(year)
        else:
            raise ValueError

        return year, month, day

    def _parse_with_month_names(self, raw: str) -> tuple[int, int, int]:  # noqa: C901
        # Cleaning from 1st, 2nd, 3rd and etc.
        cleaned = sub(self.ordinal_suffix_pattern, "", raw, flags=IGNORECASE)
        tokens = [token for token in split(self.token_split_pattern, cleaned) if token]

        month_index = None
        month_value = None
        numeric_tokens: list[tuple[int, int]] = []

        for index, token in enumerate(tokens):
            lookup_key = token.lower()
            if lookup_key in settings.normalizer.month_map:
                if month_index is not None:
                    raise ValueError("Ambiguous month tokens in date of birth value")
                month_index = index
                month_value = settings.normalizer.month_map[lookup_key]
            elif token.isdigit():
                numeric_tokens.append((index, int(token)))
            else:
                raise ValueError

        if month_index is None or month_value is None:
            raise ValueError
        if len(numeric_tokens) < 2:
            raise ValueError

        year_index, year_value = self._select_year(month_index, numeric_tokens)
        year = self._expand_year(year_value)

        remaining = [(idx, value) for idx, value in numeric_tokens if idx != year_index]
        left = [item for item in remaining if item[0] < month_index]
        right = [item for item in remaining if item[0] > month_index]

        if left and right:
            raise ValueError

        if left:
            day = left[-1][1]
        elif right:
            day = right[0][1]
        elif remaining:
            day = remaining[0][1]
        else:
            raise ValueError

        return year, month_value, day

    def _select_year(self, month_index: int, numeric_tokens: list[tuple[int, int]]) -> tuple[int, int]:
        for index, value in numeric_tokens:
            if value >= 1000:
                return index, value

        right_side = [(idx, val) for idx, val in numeric_tokens if idx > month_index]
        if right_side:
            return right_side[-1]

        return numeric_tokens[-1]

    def _expand_year(self, year: int) -> int:
        if year < 100:
            base_century = settings.normalizer.base_year
            next_century = base_century + 100
            return (next_century + year) if year <= self.pivot_year else (base_century + year)
        return year

    def _validate_or_swap(self, year: int, month: int, day: int) -> tuple[int, int, int]:
        if 1 <= month <= 12:
            _, month_days = monthrange(year, month)
            if 1 <= day <= month_days:
                return year, month, day

        if 1 <= day <= 12:
            _, swapped_days = monthrange(year, day)
            if 1 <= month <= swapped_days:
                return year, day, month

        raise ValueError
