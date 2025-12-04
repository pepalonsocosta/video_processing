from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import httpx
import os
import shutil
import uuid

app = FastAPI(
    title="Seminar2 Gateway",
    description="Gateway for S2 MPEG4 endpoints",
    version="0.1.0"
)

# Service URLs (from docker-compose)
EXERCISE_1_URL = "http://video-resolution:8000"
EXERCISE_2_URL = "http://video-chroma:8000"
EXERCISE_3_URL = "http://video-info:8000"
EXERCISE_4_URL = "http://video-audio:8000"
EXERCISE_5_URL = "http://video-tracks:8000"
EXERCISE_6_URL = "http://video-macroblocks:8000"
SHARED_DIR = "/app/shared"

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/video/resolution")
async def change_resolution(
    file: UploadFile = File(...),
    width: int = Form(...),
    height: int = Form(...)
):
    # Get file extension and generate a unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join(SHARED_DIR, unique_filename)

    # Create shared directory if it doesn't exist
    os.makedirs(SHARED_DIR, exist_ok=True)

    # Save uploaded file to shared volume
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file")
    
    # Call video-resolution service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EXERCISE_1_URL}/process",
                json={
                    "video_path": unique_filename,
                    "width": width,
                    "height": height
                },
                timeout=300.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Return the processed file
            output_path = os.path.join(SHARED_DIR, result["output_path"])
            if os.path.exists(output_path):
                return FileResponse(
                    path=output_path,
                    filename=result["output_path"],
                    media_type="video/mp4"
                )
            else:
                raise HTTPException(status_code=500, detail="Output file not found")
                
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"Error processing video")

@app.post("/api/video/chroma")
async def change_chroma_subsampling(
    file: UploadFile = File(...),
    chroma_format: str = Form(...)
):
    """
    Change chroma subsampling of a video.
    
    Common chroma formats:
    - yuv420p (4:2:0) - most common, good compression
    - yuv422p (4:2:2) - better quality, larger file
    - yuv444p (4:4:4) - best quality, largest file
    - yuv420p10le (10-bit 4:2:0) - high quality with compression
    """
    # Get file extension and generate a unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join(SHARED_DIR, unique_filename)

    # Create shared directory if it doesn't exist
    os.makedirs(SHARED_DIR, exist_ok=True)

    # Save uploaded file to shared volume
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file")
    
    # Call video-chroma service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EXERCISE_2_URL}/process",
                json={
                    "video_path": unique_filename,
                    "chroma_format": chroma_format
                },
                timeout=300.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Return the processed file
            output_path = os.path.join(SHARED_DIR, result["output_path"])
            if os.path.exists(output_path):
                return FileResponse(
                    path=output_path,
                    filename=result["output_path"],
                    media_type="video/mp4"
                )
            else:
                raise HTTPException(status_code=500, detail="Output file not found")
                
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"Error processing video")

@app.post("/api/video/info")
async def get_video_info(
    file: UploadFile = File(...)
):
    """
    Get video information and return at least 5 relevant data points.
    Returns JSON with video metadata including duration, resolution, frame rate, codec, bitrate, etc.
    """
    # Get file extension and generate a unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join(SHARED_DIR, unique_filename)

    # Create shared directory if it doesn't exist
    os.makedirs(SHARED_DIR, exist_ok=True)

    # Save uploaded file to shared volume
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file")
    
    # Call video-info service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EXERCISE_3_URL}/process",
                json={
                    "video_path": unique_filename
                },
                timeout=300.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Return the video info as JSON
            return JSONResponse(content=result)
                
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"Error getting video info")

@app.post("/api/video/bbb-container")
async def create_bbb_container(
    file: UploadFile = File(...)
):
    """
    Create BBB container with 20 seconds video and multiple audio tracks:
    - AAC mono track
    - MP3 stereo track with lower bitrate
    - AC3 codec track
    All packaged in a single MP4 file.
    """
    # Get file extension and generate a unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join(SHARED_DIR, unique_filename)

    # Create shared directory if it doesn't exist
    os.makedirs(SHARED_DIR, exist_ok=True)

    # Save uploaded file to shared volume
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file")
    
    # Call video-audio service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EXERCISE_4_URL}/process",
                json={
                    "video_path": unique_filename
                },
                timeout=300.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Return the processed file
            output_path = os.path.join(SHARED_DIR, result["output_path"])
            if os.path.exists(output_path):
                return FileResponse(
                    path=output_path,
                    filename=result["output_path"],
                    media_type="video/mp4"
                )
            else:
                raise HTTPException(status_code=500, detail="Output file not found")
                
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"Error processing video")

@app.post("/api/video/tracks")
async def count_tracks(
    file: UploadFile = File(...)
):
    """
    Read tracks from an MP4 container and return how many tracks it contains.
    Returns JSON with total tracks count and breakdown by type (video, audio, subtitle, other).
    """
    # Get file extension and generate a unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join(SHARED_DIR, unique_filename)

    # Create shared directory if it doesn't exist
    os.makedirs(SHARED_DIR, exist_ok=True)

    # Save uploaded file to shared volume
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file")
    
    # Call video-tracks service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EXERCISE_5_URL}/process",
                json={
                    "video_path": unique_filename
                },
                timeout=300.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Return the track information as JSON
            return JSONResponse(content=result)
                
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"Error counting tracks")

@app.post("/api/video/macroblocks-mv")
async def visualize_macroblocks_mv(
    file: UploadFile = File(...)
):
    """
    Create a video output showing macroblocks and motion vectors.
    Uses FFmpeg codecview filter to visualize motion vectors and macroblock types.
    """
    # Get file extension and generate a unique filename
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join(SHARED_DIR, unique_filename)

    # Create shared directory if it doesn't exist
    os.makedirs(SHARED_DIR, exist_ok=True)

    # Save uploaded file to shared volume
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file")
    
    # Call video-macroblocks service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EXERCISE_6_URL}/process",
                json={
                    "video_path": unique_filename
                },
                timeout=300.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Return the processed file
            output_path = os.path.join(SHARED_DIR, result["output_path"])
            if os.path.exists(output_path):
                return FileResponse(
                    path=output_path,
                    filename=result["output_path"],
                    media_type="video/mp4"
                )
            else:
                raise HTTPException(status_code=500, detail="Output file not found")
                
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"Error processing video")

