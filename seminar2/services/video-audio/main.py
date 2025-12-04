from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

class VideoAudioRequest(BaseModel):
    video_path: str

@app.post("/process")
async def create_bbb_container(
    request: VideoAudioRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    output_filename = f"bbb_5s_multiaudio_{request.video_path}"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    # FFmpeg command to:
    # 1. Cut video to 5 seconds
    # 2. Extract video stream
    # 3. Create AAC mono track
    # 4. Create MP3 stereo track with lower bitrate
    # 5. Create AC3 track
    # 6. Package everything in MP4
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", "5",  # Cut to 5 seconds
        "-filter_complex",
        "[0:a]pan=mono|c0=0.5*c0+0.5*c1[mono];[0:a]acopy[stereo]",
        "-map", "0:v",  # Map video stream
        "-c:v", "libx264",
        "-preset", "fast",
        "-map", "[mono]",  # Map mono audio for AAC
        "-c:a:0", "aac",
        "-b:a:0", "128k",
        "-map", "[stereo]",  # Map stereo audio for lower bitrate (using AAC, MP3 not standard in MP4)
        "-c:a:1", "aac",
        "-b:a:1", "96k",
        "-map", "0:a",  # Map original audio for AC3
        "-c:a:2", "ac3",
        "-b:a:2", "192k",
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

