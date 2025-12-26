from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
import os
import logging

from app.core import VideoProcessor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["video"])
processor = VideoProcessor()

class DownloadRequest(BaseModel):
    """Video download request model"""
    url: HttpUrl = Field(..., description="Video URL for download")
    format: Optional[str] = Field(
        "best", 
        description="Video format (best, worst, bestvideo+bestaudio, и т.д.)"
    )
    extract_audio: Optional[bool] = Field(
        False, 
        description="Extract audio only"
    )

class ConvertRequest(BaseModel):
    """Video conversion request model"""
    filename: str = Field(..., description="File name for conversion")
    output_format: Optional[str] = Field(
        "mp4", 
        description="Output format (mp4, avi, mov, и т.д.)"
    )
    resolution: Optional[str] = Field(
        None, 
        description="Resolution (e.g.: 1280x720)"
    )

class AudioExtractRequest(BaseModel):
    """Request model for audio extraction"""
    filename: str = Field(..., description="Video file name")
    audio_format: Optional[str] = Field(
        "mp3", 
        description="Audio format (mp3, wav, aac)"
    )

@router.get("/info")
async def get_video_info(url: str = Query(..., description="Video URL")):
    """Get information about the video"""
    try:
        info = processor.get_video_info(str(url))
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/download")
async def download_video(request: DownloadRequest):
    """Download video or audio"""
    result = processor.download_video(
        url=str(request.url),
        format=request.format,
        extract_audio=request.extract_audio
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result

@router.post("/convert")
async def convert_video(request: ConvertRequest):
    """Convert video"""
    input_path = os.path.join("downloads", request.filename)
    
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    result = processor.convert_video(
        input_path=input_path,
        output_format=request.output_format,
        resolution=request.resolution
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result

@router.post("/extract-audio")
async def extract_audio(request: AudioExtractRequest):
    """Extract audio from video"""
    input_path = os.path.join("downloads", request.filename)
    
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    result = processor.extract_audio(
        input_path=input_path,
        audio_format=request.audio_format
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result

@router.get("/files")
async def list_files():
    """List of downloaded files"""
    files = []
    for filename in os.listdir("downloads"):
        filepath = os.path.join("downloads", filename)
        if os.path.isfile(filepath):
            files.append({
                "name": filename,
                "size": os.path.getsize(filepath),
                "modified": os.path.getmtime(filepath)
            })
    
    return {"files": files}

@router.get("/download-file/{filename}")
async def download_file(filename: str):
    """Download file"""
    filepath = os.path.join("downloads", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/octet-stream'
    )

@router.delete("/file/{filename}")
async def delete_file(filename: str):
    """Delete file"""
    filepath = os.path.join("downloads", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(filepath)
        return {"success": True, "message": "File deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))