from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

class VideoMacroblocksRequest(BaseModel):
    video_path: str

@app.post("/process")
async def visualize_macroblocks_mv(
    request: VideoMacroblocksRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    output_filename = f"macroblocks_mv_{request.video_path}"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    # Visualize macroblocks and motion vectors using codecview filter
    cmd = [
        "ffmpeg", "-y",
        "-flags2", "+export_mvs",
        "-i", input_path,
        "-vf", "codecview=mv=pf+bf+bb:block=1",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "copy",
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

