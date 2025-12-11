from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import httpx
import os
import shutil
import uuid

app = FastAPI(
    title="Seminar2 P2 API",
    description="API for S2 P2 endpoints",
    version="0.1.0"
)

# Service URLs (from docker-compose)
CONVERTER_P2_URL = "http://converter-p2:8000"
SHARED_DIR = "/app/shared"

SUPPORTED_CODECS = {"av1", "h265", "vp8", "vp9"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/video/convert/{codec}")
async def convert_video(
    codec: str,
    file: UploadFile = File(...),
):
    # Validate codec
    if codec.lower() not in SUPPORTED_CODECS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported codec: {codec}. Supported codecs: {', '.join(SUPPORTED_CODECS)}"
        )
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
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONVERTER_P2_URL}/process/{codec.lower()}",
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