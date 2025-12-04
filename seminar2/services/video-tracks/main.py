from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import json

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

class VideoTracksRequest(BaseModel):
    video_path: str

@app.post("/process")
async def count_tracks(
    request: VideoTracksRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    
    cmd = [
        "ffprobe",
        "-v", "error",
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
        
        # Count tracks by type
        video_tracks = 0
        audio_tracks = 0
        subtitle_tracks = 0
        other_tracks = 0
        
        for stream in probe_data.get("streams", []):
            codec_type = stream.get("codec_type", "").lower()
            if codec_type == "video":
                video_tracks += 1
            elif codec_type == "audio":
                audio_tracks += 1
            elif codec_type == "subtitle":
                subtitle_tracks += 1
            else:
                other_tracks += 1
        
        total_tracks = len(probe_data.get("streams", []))
        
        return {
            "status": "success",
            "filename": os.path.basename(request.video_path),
            "total_tracks": total_tracks,
            "video_tracks": video_tracks,
            "audio_tracks": audio_tracks,
            "subtitle_tracks": subtitle_tracks,
            "other_tracks": other_tracks
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"FFprobe error: {e.stderr}"
        )

