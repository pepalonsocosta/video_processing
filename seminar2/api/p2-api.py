from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import shutil
import uuid

app = FastAPI(
    title="Seminar2 P2 API",
    description="API for S2 P2 endpoints",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CONVERTER_P2_URL = "http://converter-p2:8000"
ENCODING_LADDER_URL = "http://encoding-ladder:8000"
SHARED_DIR = "/app/shared"
SUPPORTED_CODECS = {"av1", "h265", "vp8", "vp9"}

def _save_uploaded_file(file: UploadFile) -> tuple[str, str]:
    """Save uploaded file and return unique filename and full path."""
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join(SHARED_DIR, unique_filename)
    os.makedirs(SHARED_DIR, exist_ok=True)
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return unique_filename, input_path

def _validate_codec(codec: str):
    """Validate codec is supported."""
    if codec.lower() not in SUPPORTED_CODECS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported codec: {codec}. Supported: {', '.join(SUPPORTED_CODECS)}"
        )

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/video/convert/{codec}")
async def convert_video(codec: str, file: UploadFile = File(...)):
    _validate_codec(codec)
    unique_filename, input_path = _save_uploaded_file(file)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CONVERTER_P2_URL}/process/{codec.lower()}",
                json={"video_path": unique_filename},
                timeout=300.0
            )
            response.raise_for_status()
            result = response.json()
            output_path = os.path.join(SHARED_DIR, result["output_path"])
            
            if not os.path.exists(output_path):
                raise HTTPException(status_code=500, detail="Output file not found")
            
            return FileResponse(
                path=output_path,
                filename=result["output_path"],
                media_type="video/mp4"
            )
    except httpx.HTTPError:
        raise HTTPException(status_code=500, detail="Error processing video")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@app.post("/api/video/encoding-ladder")
async def encoding_ladder(
    file: UploadFile = File(...),
    codec: str = Form(...),
    resolutions: str = Form(...)
):
    _validate_codec(codec)
    resolutions_list = [r.strip() for r in resolutions.split(",")]
    unique_filename, input_path = _save_uploaded_file(file)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ENCODING_LADDER_URL}/process",
                json={
                    "video_path": unique_filename,
                    "codec": codec.lower(),
                    "resolutions": resolutions_list
                },
                timeout=600.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        raise HTTPException(status_code=500, detail="Error creating encoding ladder")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)