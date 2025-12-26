#  yt dlp ffmpeg API

A RESTful API service built with FastAPI, yt-dlp, and FFmpeg for downloading, converting, and processing videos. Containerized with Docker for easy deployment.

## 🚀 Features

- **Video Information**: Get detailed metadata about any video from supported platforms
- **Download Videos/Audio**: Download videos in various formats or extract audio only
- **Video Conversion**: Convert videos between formats and resolutions
- **Audio Extraction**: Extract audio from video files
- **File Management**: List, download, and delete processed files
- **Docker Support**: Fully containerized with Docker and Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- For local development: Python 3.11+

## 🛠️ Installation

### Using Docker (Recommended)

1. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd yt-dlp-ffmpeg-api-service
```

2. Build and run the container:
```bash
docker-compose up --build -d
```

3. The API will be available at `http://localhost:8181`

### Local Development Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install FFmpeg:
- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

3. Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8181 --reload
```

## 📖 API Documentation

Once running, access the interactive API documentation:
- Swagger UI: `http://localhost:8181/docs`
- OpenApi: `http://localhost:8181/openapi.json`

## 🎯 API Endpoints

### Health Check
```http
GET /health
```
Returns the service health status.

### Get Video Information
```http
GET /api/v1/info?url={video_url}
```
Retrieves metadata about a video.

**Example:**
```bash
curl "http://localhost:8181/api/v1/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Download Video
```http
POST /api/v1/download
```
Downloads a video or audio from a URL.

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "best",
    "extract_audio": false
}
```

**Special Formats for Reddit/Platforms with Separate Streams:**
```json
{
    "url": "https://www.reddit.com/r/...",
    "format": "bestvideo+bestaudio",
    "extract_audio": false
}
```

**Examples:**
```bash
# Download video
curl -X POST "http://localhost:8181/api/v1/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Download audio only
curl -X POST "http://localhost:8181/api/v1/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "extract_audio": true}'

# For Reddit videos with separate audio/video streams
curl -X POST "http://localhost:8181/api/v1/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.reddit.com/r/videos/comments/...", "format": "bestvideo+bestaudio"}'
```

### Convert Video
```http
POST /api/v1/convert
```
Converts a video to a different format or resolution.

**Request Body:**
```json
{
    "filename": "video.mp4",
    "output_format": "mp4",
    "resolution": "1280x720"
}
```

**Examples:**
```bash
# Convert to 720p
curl -X POST "http://localhost:8181/api/v1/convert" \
  -H "Content-Type: application/json" \
  -d '{"filename": "video.mp4", "resolution": "1280x720"}'

# Convert to WebM format
curl -X POST "http://localhost:8181/api/v1/convert" \
  -H "Content-Type: application/json" \
  -d '{"filename": "video.mp4", "output_format": "webm"}'
```

### Extract Audio
```http
POST /api/v1/extract-audio
```
Extracts audio from a video file.

**Request Body:**
```json
{
    "filename": "video.mp4",
    "audio_format": "mp3"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8181/api/v1/extract-audio" \
  -H "Content-Type: application/json" \
  -d '{"filename": "video.mp4", "audio_format": "mp3"}'
```

### List Files
```http
GET /api/v1/files
```
Lists all downloaded and processed files.

**Example:**
```bash
curl "http://localhost:8181/api/v1/files"
```

### Download File
```http
GET /api/v1/download-file/{filename}
```
Downloads a specific file.

**Example:**
```bash
curl "http://localhost:8181/api/v1/download-file/video.mp4" --output video.mp4
```

### Delete File
```http
DELETE /api/v1/file/{filename}
```
Deletes a file from the server.

**Example:**
```bash
curl -X DELETE "http://localhost:8181/api/v1/file/video.mp4"
```

## 🐳 Docker Configuration

### Dockerfile
The application uses a multi-stage build for optimal image size:
- Base image: Python 3.11-slim
- Installs system dependencies (FFmpeg)
- Copies application code and installs Python dependencies
- Exposes port 8181

### Docker Compose
The `docker-compose.yml` file provides:
- Volume mapping for persistent storage (`./downloads:/app/downloads`)
- Health checks
- Auto-restart policy

### Environment Variables
Create a `.env` file for configuration:

```env
DOWNLOAD_DIR=downloads
MAX_FILE_SIZE=10737418240  # 10GB
ALLOWED_DOMAINS=youtube.com,vimeo.com,twitch.tv,reddit.com
```

## 📁 Project Structure

```
yt-dlp-ffmpeg-api-service/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .env.example
├── downloads/              # Downloaded files (created automatically)
└── app/
    ├── __init__.py
    ├── main.py            # FastAPI application setup
    ├── api/
    │   ├── __init__.py
    │   └── endpoints.py   # API route handlers
    └── core/
        ├── __init__.py
        └── video_processor.py  # Business logic with yt-dlp and FFmpeg
```

## 🔧 Troubleshooting

### Common Issues

1. **"Requested format is not available" error with Reddit videos**
   - Use `"format": "bestvideo+bestaudio"` in your download request
   - Reddit often serves video and audio as separate streams

2. **FFmpeg not found errors**
   - Ensure FFmpeg is installed in the Docker container (included in Dockerfile)
   - For local development, install FFmpeg system-wide

3. **Permission issues with downloads directory**
   ```bash
   chmod -R 777 downloads
   ```

4. **Docker build fails**
   - Check Docker daemon is running
   - Ensure sufficient disk space
   - Check network connectivity for pulling base images

### Logs and Debugging

View Docker container logs:
```bash
docker-compose logs -f
```

Check container health:
```bash
docker-compose ps
```

## 📝 Supported Platforms

The API supports all platforms supported by yt-dlp, including:
- YouTube
- Vimeo
- Twitter
- Reddit
- TikTok
- Instagram
- And 1000+ more sites

## 🔒 Security Notes

⚠️ **Important**: This API is designed for development and personal use. For production:

1. Add authentication/authorization
2. Implement rate limiting
3. Set up proper CORS policies
4. Use HTTPS
5. Monitor and limit file sizes
6. Add request validation and sanitization

## 📄 License

This project is provided for educational and personal use. Ensure you comply with the terms of service of video platforms and respect copyright laws.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Ensure all prerequisites are met
4. Check container logs for errors

---

**Note**: Always respect copyright laws and terms of service of video platforms. This tool is intended for personal use and downloading content you have rights to access.