import logging
import os
import subprocess
import uuid
from typing import Any, Dict, Optional

import yt_dlp

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Class for processing video using yt-dlp and ffmpeg"""

    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        logger.info(f"VideoProcessor initialized with download_dir: {download_dir}")

    def get_video_info(self, url: str) -> Dict:
        """Get information about the video"""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "duration": info.get("duration"),
                "formats": info.get("formats", []),
                "thumbnail": info.get("thumbnail"),
                "uploader": info.get("uploader"),
            }

    def download_video(
        self,
        url: str,
        format: Optional[str] = None, 
        extract_audio: bool = False,
    ) -> Dict:
        """Download video or audio"""
        unique_id = str(uuid.uuid4())
        output_template = os.path.join(self.download_dir, f"{unique_id}.%(ext)s")

        # Basic settings
        ydl_opts = {
            "outtmpl": output_template,
            "quiet": False,
            "progress_hooks": [self._progress_hook],
            "merge_output_format": "mp4",  # Specify the format to merge into
        }

        # Key change: if format is not specified, do not pass the “format” parameter.
        # This allows yt-dlp to use its smart default selector (bv*+ba/b).
        if format:
            ydl_opts["format"] = format

        if extract_audio:
            ydl_opts.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                    "postprocessor_args": ["-ar", "16000"],
                    "prefer_ffmpeg": True,
                }
            )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                if extract_audio:
                    filename = filename.rsplit(".", 1)[0] + ".mp3"

                return {
                    "success": True,
                    "filename": os.path.basename(filename),
                    "filepath": filename,
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def convert_video(
        self,
        input_path: str,
        output_format: str = "mp4",
        resolution: Optional[str] = None,
    ) -> Dict:
        """Convert video to another format"""
        if not os.path.exists(input_path):
            return {"success": False, "error": "File not found"}

        unique_id = str(uuid.uuid4())
        output_path = os.path.join(self.download_dir, f"{unique_id}.{output_format}")

        cmd = ["ffmpeg", "-i", input_path]

        if resolution:
            cmd.extend(["-vf", f"scale={resolution}"])

        cmd.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                output_path,
                "-y",
            ]
        )

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return {
                "success": True,
                "output_file": os.path.basename(output_path),
                "output_path": output_path,
                "message": "Conversion completed",
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def extract_audio(self, input_path: str, audio_format: str = "mp3") -> Dict:
        """Extract audio from video"""
        if not os.path.exists(input_path):
            return {"success": False, "error": "File not found"}

        unique_id = str(uuid.uuid4())
        output_path = os.path.join(self.download_dir, f"{unique_id}.{audio_format}")

        cmd = [
            "ffmpeg",
            "-i",
            input_path,
            "-vn",  # no video
            "-acodec",
            "libmp3lame" if audio_format == "mp3" else "copy",
            "-ab",
            "192k",
            "-ar",
            "44100",
            "-y",
            output_path,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            return {
                "success": True,
                "output_file": os.path.basename(output_path),
                "output_path": output_path,
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def _progress_hook(self, d):
        """WebHook for tracking download progress"""
        if d["status"] == "downloading":
            print(f"Downloading: {d.get('_percent_str', 'N/A')}")
        elif d["status"] == "finished":
            print("Download completed, post-processing...")
