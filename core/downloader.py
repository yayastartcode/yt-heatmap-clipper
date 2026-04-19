"""
Video downloader module
Handles video segment downloading using yt-dlp
"""
import os
import sys
import subprocess
from typing import Optional, Callable

import config


def download_video_segment(
    video_id: str,
    start: float,
    end: float,
    output_file: str,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Download a specific segment of a YouTube video.
    
    Args:
        video_id: YouTube video ID
        start: Start time in seconds
        end: End time in seconds
        output_file: Path to save the downloaded segment
        progress_callback: Optional callback function for progress updates
        
    Returns:
        True if successful, False otherwise
    """
    if progress_callback:
        progress_callback(config.PROGRESS_DOWNLOAD, 0, f"Downloading segment {start}s-{end}s")
    
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--force-ipv4",
        "--quiet", "--no-warnings",
        "--downloader", "ffmpeg",
        "--downloader-args",
        f"ffmpeg_i:-ss {start} -to {end} -hide_banner -loglevel error",
        "-f",
        "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "-o", output_file,
        f"https://youtu.be/{video_id}"
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if not os.path.exists(output_file):
            if progress_callback:
                progress_callback(config.PROGRESS_ERROR, 0, "Download failed: file not created")
            return False

        if progress_callback:
            progress_callback(config.PROGRESS_DOWNLOAD, 100, "Download complete")
        
        return True

    except subprocess.TimeoutExpired:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, "Download timeout")
        return False
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"Download failed: {error_msg}")
        return False
    except Exception as e:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"Download error: {str(e)}")
        return False


def update_ytdlp() -> bool:
    """
    Update yt-dlp to the latest version.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60
        )
        return True
    except Exception:
        return False
