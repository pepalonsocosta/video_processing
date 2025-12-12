from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from video_codecs.av1 import AV1
from video_codecs.h265 import H265
from video_codecs.vp8 import VP8
from video_codecs.vp9 import VP9
import os

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"
CODEC_CLASSES = {"av1": AV1, "h265": H265, "vp8": VP8, "vp9": VP9}

class ConvertRequest(BaseModel):
    video_path: str

def _get_output_filename(video_path: str, codec: str) -> str:
    """Generate output filename based on codec requirements."""
    if codec == "vp8":
        base_name = os.path.splitext(video_path)[0]
        return f"converted_{base_name}.webm"
    return f"converted_{video_path}"

@app.post("/process/{codec}")
async def convert_video(codec: str, request: ConvertRequest):
    if codec.lower() not in CODEC_CLASSES:
        raise HTTPException(status_code=400, detail=f"Unsupported codec: {codec}")
    
    input_path = os.path.join(SHARED_DIR, request.video_path)
    output_filename = _get_output_filename(request.video_path, codec.lower())
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    try:
        CODEC_CLASSES[codec.lower()].encode(input_path, output_path)
        return {"status": "success", "output_path": output_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encoding video: {e}")