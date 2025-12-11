from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from video_codecs.av1 import AV1
from video_codecs.h265 import H265
from video_codecs.vp8 import VP8
from video_codecs.vp9 import VP9
import os

app = FastAPI(version="0.1.0")

SHARED_DIR = "/app/shared"

class ConvertRequest(BaseModel):
    video_path: str

@app.post("/process/av1")
async def convert_av1(
    request: ConvertRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    output_filename = f"converted_{request.video_path}"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    
    
    try:
        AV1.encode(input_path, output_path)
        return {
            "status": "success",
            "output_path": output_filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error encoding video: {e}"
        )

@app.post("/process/h265")
async def convert_h265(
    request: ConvertRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    output_filename = f"converted_{request.video_path}"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    
    
    try:
        H265.encode(input_path, output_path)
        return {
            "status": "success",
            "output_path": output_filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error encoding video: {e}"
        )

@app.post("/process/vp8")
async def convert_vp8(
    request: ConvertRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    # VP8 must use .webm container, not .mp4
    base_name = os.path.splitext(request.video_path)[0]
    output_filename = f"converted_{base_name}.webm"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    
    
    try:
        VP8.encode(input_path, output_path)
        return {
            "status": "success",
            "output_path": output_filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error encoding video: {e}"
        )

@app.post("/process/vp9")
async def convert_vp9(
    request: ConvertRequest
):
    input_path = os.path.join(SHARED_DIR, request.video_path)
    output_filename = f"converted_{request.video_path}"
    output_path = os.path.join(SHARED_DIR, output_filename)
    
    
    
    try:
        VP9.encode(input_path, output_path)
        return {
            "status": "success",
            "output_path": output_filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error encoding video: {e}"
        )