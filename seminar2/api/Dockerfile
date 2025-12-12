FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY p2-api.py ./

# Install dependencies
RUN uv pip install --system --no-cache .

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["fastapi", "run", "p2-api.py", "--host", "0.0.0.0", "--port", "8000"]

