# Hey! This is our report for 02 - P1. Here we will explain the aproach we though it was better for each exercise and how we implemented.

### Framework

As in S1 we are using uv python manager to handle in a nicer way the dependencies.

For the http api we chose to go with fastapi as it was the one that provided the cleaner and shorter way to define endpoints etc

## Ex 1

For this exercise we created a scaffold for what will be our api contaier wich will serve our program and expose some of the methods we implemented on S1.
As we said we went with fastapi wich allows us to define endpoints like this:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
```

We used uv also for the this container as well, we just created an enpoint for the health to see if our app is working.

We can run the app in dev mode running:

```bash
uv run fastapi dev main.py
```

Then we created a dockerfile to contarize the application, sinde the docker file we just copy the necesary files and run the fastapi framework with uv

We did it like this:

```bash
sudo docker build -t practice1-api .
sudo docker run -p 8000:8000 practice1-api
```

## Ex 2

For this exercise we needed to put ffmpeg inside a Docker container. We created a simple Dockerfile that installs ffmpeg on an Ubuntu base image.

We kept it as simple as possible:

```dockerfile
FROM ubuntu:latest

RUN apt-get update && apt-get install -y ffmpeg

CMD ["ffmpeg"]
```

This creates a container with ffmpeg installed and ready to use. We can build and test it like this:

```bash
cd practice1/ffmpeg
sudo docker build -t ffmpeg-container .
sudo docker run --rm ffmpeg-container -version
```

The container will be used later in exercise 5 when we need to call ffmpeg from the API for video/image processing.

## Ex 3

For this exercise we needed to include all the previous work from S1 inside the new API. We organized it by creating an `app/` folder where we placed all the S1 classes:

- `app/dct_class.py` - DCT encoding/decoding class
- `app/dwt_class.py` - DWT encoding/decoding class
- `app/first_seminar.py` - Seminar1 class with all the methods (RGB/YUV conversion, image compression, serpentine, run-length encoding, etc.)

We also copied and adapted all the unit tests from S1 into a `tests/` folder, updating the imports to work with the new structure:

- `tests/test_dct_class.py` - Tests for DCT class
- `tests/test_dwt_class.py` - Tests for DWT class
- `tests/test_first_seminar.py` - Tests for Seminar1 class

We updated the `pyproject.toml` to include the necessary dependencies:

- `numpy>=2.3.5` - For DCT/DWT operations
- `pywavelets>=1.9.0` - For DWT implementation
- `pytest>=7.0.0` and `pytest-cov>=4.0.0` - For running tests

We also updated the Dockerfile to copy the `app/` folder so all the S1 code is available inside the container.

To run the tests:

```bash
cd practice1/api
uv sync
uv run pytest
```

All the S1 functionality is now integrated and ready to be exposed via API endpoints in the next exercise.

## Ex 4

For this exercise we needed to create at least 2 endpoints that process some actions from S1. We created two endpoints that expose S1 functionality via HTTP:

Endpoint: POST `/api/dct/encode`

This endpoint uses the `DCT.encode()` method from S1 to encode an 8x8 block of pixel values using Discrete Cosine Transform.

Endpoint 2: POST `/api/rgb-to-yuv`

This endpoint uses the `Seminar1.rgb_to_yuv()` method from S1 to convert RGB color values to YUV color space.

**Request:**

```json
{
  "r": 120,
  "g": 200,
  "b": 80
}
```

**Response:**

```json
{
  "y": 155.48,
  "u": 87.16,
  "v": 101.4
}
```

### Endpoint 3: POST `/api/compress-image`

This endpoint uses the `Seminar1.reduce_quality()` method from S1 to compress images using FFMPEG. It demonstrates file upload and download functionality.

How it works:

1. File Upload: The endpoint accepts an image file using FastAPI's `UploadFile` parameter. FastAPI handles multipart/form-data automatically.

2. File Saving: The uploaded file is saved to the shared volume (`/app/shared/`) so it can be accessed by both the API and FFMPEG containers.

3. Processing: The `reduce_quality()` method is called, which uses FFMPEG (running in a Docker container) to compress the image.

4. File Response: Instead of returning JSON, the endpoint returns the compressed image file directly using FastAPI's `FileResponse`, which allows the client to download the processed image.

Request:

- Upload a file using multipart/form-data
- Optional query parameter: `compression_factor` (default: 32)

Response:

- Returns the compressed image file directly (binary)

Example usage (saving the ouput file to a relative path)

```bash
curl -X POST "http://localhost:8000/api/compress-image?compression_factor=32" \
  -F "file=@image.jpg" \
  -o compressed_output.jpg
```

We used Pydantic models for request/response validation, which provides automatic validation and documentation. FastAPI automatically generates interactive API documentation at `/docs` where you can test these endpoints.

To test the endpoints:

```bash
# Start the API
uv run fastapi dev main.py

# Or with Docker
sudo docker build -t practice1-api .
sudo docker run -p 8000:8000 practice1-api

```

## Ex 5

For this exercise we needed to use docker-compose to launch both the API and FFMPEG containers and make them interact. The API should call the FFMPEG Docker container for video/image conversions.

### Docker Compose Setup

We created a `docker-compose.yml` file that orchestrates both services:

Key points:

- Both containers share a `shared/` volume for file exchange
- API container has access to Docker socket to run `docker exec` commands
- FFMPEG container runs in background mode (`tail -f /dev/null`)

### Utility Function

We created a reusable utility function `app/docker_utils.py` that wraps the docker exec command:

```python
def run_ffmpeg_in_container(ffmpeg_args, container_name="practice1-ffmpeg-1"):
    cmd = ['docker', 'exec', container_name, 'ffmpeg'] + ffmpeg_args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result
```

This function is used by `reduce_quality()` and `convert_to_bw_max_compression()` methods in `Seminar1` class, which now call FFMPEG through the Docker container instead of directly.

### Updated Dockerfile

The API Dockerfile now installs the Docker client so it can execute docker commands:

```dockerfile
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*
```

### Running with Docker Compose

To start both containers:

```bash
cd practice1
sudo docker-compose up --build
```

This will build and run teh cntainers
The API is now available at `http://localhost:8000` and can process images/videos using FFMPEG running in its own container.
