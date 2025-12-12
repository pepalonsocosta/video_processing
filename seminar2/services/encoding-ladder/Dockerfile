FROM python:3.12-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the service
COPY services/encoding-ladder/main.py ./

# Copy the video_codecs directory
COPY video_codecs/ ./video_codecs/

RUN pip install fastapi[standard]

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

