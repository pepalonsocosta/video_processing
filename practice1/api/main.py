from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from app.dct_class import DCT
from app.first_seminar import Seminar1
import numpy as np
import os
import shutil

app = FastAPI(
    title="Practice1 API",
    description="P1 - API and Dockerization",
    version="0.1.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


class DCTEncodeRequest(BaseModel):
    block: List[List[int]]


class DCTEncodeResponse(BaseModel):
    coefficients: List[List[float]]


class RGBToYUVRequest(BaseModel):
    r: int
    g: int
    b: int


class RGBToYUVResponse(BaseModel):
    y: float
    u: float
    v: float


@app.post("/api/dct/encode", response_model=DCTEncodeResponse)
async def dct_encode(request: DCTEncodeRequest):

    block = np.array(request.block, dtype=np.uint8)
    coefficients = DCT.encode(block)
    return DCTEncodeResponse(coefficients=coefficients.tolist())


@app.post("/api/rgb-to-yuv", response_model=RGBToYUVResponse)
async def rgb_to_yuv(request: RGBToYUVRequest):

    y, u, v = Seminar1.rgb_to_yuv(request.r, request.g, request.b)
    return RGBToYUVResponse(y=y, u=u, v=v)


@app.post("/api/compress-image")
async def compress_image(
    file: UploadFile = File(...),
    compression_factor: int = 32
):
    # Save uploaded file to shared volume
    shared_dir = "/app/shared"
    os.makedirs(shared_dir, exist_ok=True)
    
    input_filename = file.filename
    output_filename = f"compressed_{file.filename}"
    
    # Save uploaded file
    input_path = os.path.join(shared_dir, input_filename)
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # reduce_quality handles the FFMPEG call in container
    Seminar1.reduce_quality(input_filename, output_filename, compression_factor)
    
    # Return the compressed file
    output_path = os.path.join(shared_dir, output_filename)
    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type="image/jpeg"
    )

