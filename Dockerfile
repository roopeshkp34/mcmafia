#Python3.14
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

# Install uv (dependency manager for python)
RUN pip install --no-cache-dir uv

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    clang \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files for dependency resolution
COPY pyproject.toml uv.lock /app/

# Install dependencies using uv
RUN uv sync --no-dev

# Copy the current directory contents into the container at /app
COPY app /app/app
# COPY alembic /app/alembic
COPY prestart.py start.sh main.py /app/

# Make start-dev.sh executable
RUN chmod +X /app/start.sh

CMD ["sh", "/app/start.sh"]
