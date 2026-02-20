#!/usr/bin/env sh
set -e

# Use virtualenv packages
export PATH="/app/.venv/bin:$PATH"

echo "Running prestart checks..."
python prestart.py

# echo "Running Alembic migrations..."
# alembic upgrade head

echo "Starting app on port ${PORT:-8000}..."
exec uvicorn main:app --reload --host 0.0.0.0 --port ${PORT:-8000}
