FROM python:3.12-slim

# Install uv and docker client
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY main.py ./
COPY app/ ./app/

# Install dependencies with uv (installs from pyproject.toml)
RUN uv pip install --system --no-cache .

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]

