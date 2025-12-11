from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from video_codecs.av1 import AV1
from video_codecs.h265 import H265
from video_codecs.vp8 import VP8
from video_codecs.vp9 import VP9
import os

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

# Resolution mapping
RESOLUTIONS = {
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080)
}

CODEC_CLASSES = {
    "av1": AV1,
    "h265": H265,
    "vp8": VP8,
    "vp9": VP9
}

class EncodingLadderRequest(BaseModel):
    video_path: str
    codec: str
    resolutions: list[str]

@app.post("/process")
async def create_encoding_ladder(
    request: EncodingLadderRequest
):
    if request.codec.lower() not in CODEC_CLASSES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported codec: {request.codec}"
        )
    
    for res in request.resolutions:
        if res.lower() not in RESOLUTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported resolution: {res}"
            )
    
    input_path = os.path.join(SHARED_DIR, request.video_path)
    codec_class = CODEC_CLASSES[request.codec.lower()]
    
    ladder = []
    base_name = os.path.splitext(request.video_path)[0]
    file_ext = os.path.splitext(request.video_path)[1]
    
    # Handle VP8/VP9 webm extension
    if request.codec.lower() in ["vp8", "vp9"]:
        file_ext = ".webm"
    
    try:
        for resolution in request.resolutions:
            width, height = RESOLUTIONS[resolution.lower()]
            output_filename = f"ladder_{request.codec.lower()}_{resolution}_{base_name}{file_ext}"
            output_path = os.path.join(SHARED_DIR, output_filename)
            
            # Call existing encode method with resolution
            codec_class.encode(input_path, output_path, width=width, height=height)
            
            # Get file size
            file_size_mb = round(os.path.getsize(output_path) / (1024 * 1024), 2)
            
            ladder.append({
                "resolution": resolution,
                "width": width,
                "height": height,
                "output_path": output_filename,
                "file_size_mb": file_size_mb
            })
        
        return {
            "status": "success",
            "codec": request.codec,
            "ladder": ladder
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating encoding ladder: {e}"
        )

