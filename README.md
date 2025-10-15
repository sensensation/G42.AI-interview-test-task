# CSV Normalization Service

Normalize contact CSVs (phone -> E.164, DOB -> `YYYY-MM-DD`) through a FastAPI endpoint.

## Quick Start

```bash
uv sync      # install deps & create .venv
make format  # runs ruff format via uv
make lint    # ruff format --check + ruff check
make test    # pytest suite (async + integration)
make start   # run the docker container with app

Make targets call `uv run` internally, so there is no need to manually activate .venv
```

## API

```
POST /api/internal/v1/upload/normalize   multipart/form-data (field: file)
```

Use /docs to make request on /upload/normalize with input_data.csv

Headers (`X-CSV-Processed`, `X-CSV-Normalized`, `X-CSV-Skipped`) report stats; body is the normalized CSV.

## Test Data & Fixtures

- `tests/resources/` – sample input & golden output.
- `tests/fixtures/` – pytest fixtures for files, services, and ASGI client.
- `tests/test_api_normalize.py` – endpoint tests.
- `tests/test_csv_service_integration.py` – service integration.
- `tests/test_data_normalizer_dob.py` – phone and DOB cases.

## Docker

```bash
make start
make stop
```

Copy `example-config.json` to `config.json` if you need custom settings.
