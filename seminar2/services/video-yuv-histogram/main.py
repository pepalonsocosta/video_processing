from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

class VideoYUVHistogramRequest(BaseModel):
    video_path: str

@app.post("/process")
async def visualize_yuv_histogram(
    request: VideoYUVHistogramRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    output_filename = f"yuv_histogram_{request.video_path}"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    # Visualize YUV histogram using histogram filter
    # Shows Y (luma), U (Cb), and V (Cr) component histograms
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "histogram=display_mode=overlay:components=7",
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

