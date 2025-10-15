#!/bin/sh
set -euo pipefail

cd /opt/app
export PYTHONPATH=/opt/app

uv run alembic upgrade head
exec uv run python -m typer manage run-server