from fastapi import FastAPI, HTTPException, Body
import subprocess
import os

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

@app.post("/process")
async def change_chroma_subsampling(
    video_path: str = Body(...),
    chroma_format: str = Body(...)
):
    """
    Change chroma subsampling of a video.
    
    Common chroma formats:
    - yuv420p (4:2:0) - most common, good compression
    - yuv422p (4:2:2) - better quality, larger file
    - yuv444p (4:4:4) - best quality, largest file
    - yuv420p10le (10-bit 4:2:0) - high quality with compression
    """
    input_path = os.path.join(SHARED_DIR, video_path)
    output_filename = f"chroma_{chroma_format}_{video_path}"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    # Validate chroma format
    valid_formats = ["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le"]
    if chroma_format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chroma format. Valid formats: {', '.join(valid_formats)}"
        )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-pix_fmt", chroma_format,
        "-c:v", "libx264",  # Use H.264 codec
        "-preset", "medium",  # Encoding preset
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "status": "success",
            "output_path": output_filename,
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"FFmpeg error: {e.stderr}"
        )

