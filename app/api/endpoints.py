from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import os
from app.core.video_processor import VideoProcessor

router = APIRouter()
processor = VideoProcessor()

class DownloadRequest(BaseModel):
    url: HttpUrl
    format: Optional[str] = "best"
    extract_audio: Optional[bool] = False

class ConvertRequest(BaseModel):
    filename: str
    output_format: Optional[str] = "mp4"
    resolution: Optional[str] = None

class AudioExtractRequest(BaseModel):
    filename: str
    audio_format: Optional[str] = "mp3"

@router.get("/info")
async def get_video_info(url: str = Query(..., description="URL видео")):
    """Получить информацию о видео"""
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
    """Скачать видео или аудио"""
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
    """Конвертировать видео"""
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
    """Извлечь аудио из видео"""
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
    """Список загруженных файлов"""
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
    """Скачать файл"""
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
    """Удалить файл"""
    filepath = os.path.join("downloads", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(filepath)
        return {"success": True, "message": "File deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))