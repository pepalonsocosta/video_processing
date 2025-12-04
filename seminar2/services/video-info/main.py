from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import json

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

class VideoInfoRequest(BaseModel):
    video_path: str

@app.post("/process")
async def get_video_info(
    request: VideoInfoRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_format",
        "-show_streams",
        "-of", "json",
        input_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        probe_data = json.loads(result.stdout)
        
        # Extract video stream
        video_stream = None
        for stream in probe_data.get("streams", []):
            if stream.get("codec_type") == "video":
                video_stream = stream
                break
        
        if not video_stream:
            raise HTTPException(
                status_code=400,
                detail="No video stream found in file"
            )
        
        format_info = probe_data.get("format", {})
        
        # Parse frame rate
        frame_rate_str = video_stream.get("r_frame_rate", "0/1")
        frame_rate = 0.0
        if '/' in frame_rate_str:
            try:
                num, den = map(int, frame_rate_str.split('/'))
                frame_rate = num / den if den != 0 else 0.0
            except (ValueError, ZeroDivisionError):
                pass
        
        # Extract 7 relevant data points
        video_info = {
            "duration": float(format_info.get("duration", 0)),
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "frame_rate": frame_rate,
            "codec_name": video_stream.get("codec_name", "unknown"),
            "bitrate": int(format_info.get("bit_rate", 0)),
            "size_mb": round(int(format_info.get("size", 0)) / (1024 * 1024), 2),
        }
        
        return {
            "status": "success",
            "video_info": video_info
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"FFprobe error: {e.stderr}"
        )
