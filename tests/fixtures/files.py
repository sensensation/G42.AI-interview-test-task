from collections.abc import Callable
from pathlib import Path
from shutil import copyfile

import pytest

_RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"


@pytest.fixture
def input_csv_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Provide a temporary copy of the sample input CSV."""
    source = _RESOURCES_DIR / "input_data.csv"
    destination_dir = tmp_path_factory.mktemp("csv-input")
    destination = destination_dir / source.name
    copyfile(source, destination)
    return destination


@pytest.fixture
def expected_csv_path() -> Path:
    """Return the path to the example CSV."""
    return _RESOURCES_DIR / "test.csv"


@pytest.fixture
def load_bytes() -> Callable[[Path], bytes]:
    """Expose a helper to read file contents as bytes."""

    def _load(path: Path) -> bytes:
        return Path(path).read_bytes()

    return _load
