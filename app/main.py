from fastapi import FastAPI
from app.api.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware
import os

# Создаем папку для загрузок если её нет
os.makedirs("downloads", exist_ok=True)

app = FastAPI(
    title="Video Processing API",
    description="API для скачивания и обработки видео с помощью yt-dlp и ffmpeg",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Video Processing API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}