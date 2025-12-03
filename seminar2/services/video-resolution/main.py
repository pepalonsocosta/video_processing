from fastapi import FastAPI, HTTPException, Body
import subprocess
import os

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

@app.post("/process")
async def change_resolution(
    video_path: str = Body(...),
    width: int = Body(...),
    height: int = Body(...)
):
    input_path = os.path.join(SHARED_DIR, video_path)
    output_filename = f"resized_{video_path}"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"scale={width}:{height}",
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
