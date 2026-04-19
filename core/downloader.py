"""
Video downloader module
Handles video segment downloading using yt-dlp with robust fallback strategies
"""
import os
import sys
import subprocess
import time
import re
from typing import Optional, Callable, Tuple
from pathlib import Path

import config


class DownloadError(Exception):
    """Custom exception for download errors with error type"""
    def __init__(self, message: str, error_type: str = config.ERROR_UNKNOWN):
        super().__init__(message)
        self.error_type = error_type


def download_video_segment(
    video_id: str,
    start: float,
    end: float,
    output_file: str,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Download a specific segment of a YouTube video with robust fallback strategies.
    
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
    
    # Try each strategy with retries
    for strategy in config.YT_DOWNLOAD_STRATEGIES:
        for attempt in range(config.MAX_RETRIES):
            try:
                if progress_callback:
                    strategy_name = strategy.replace("_", " ").title()
                    progress_callback(
                        config.PROGRESS_DOWNLOAD, 
                        10 + (attempt * 10), 
                        f"Trying {strategy_name} (attempt {attempt + 1}/{config.MAX_RETRIES})"
                    )
                
                success, error_type = _download_with_strategy(
                    video_id, start, end, output_file, strategy, progress_callback
                )
                
                if success:
                    if progress_callback:
                        progress_callback(config.PROGRESS_DOWNLOAD, 100, "Download complete")
                    return True
                
                # If it's a permanent error (not found, private, etc.), don't retry
                if error_type in [config.ERROR_NOT_FOUND, config.ERROR_PRIVATE, config.ERROR_AGE_RESTRICTED]:
                    if progress_callback:
                        progress_callback(config.PROGRESS_ERROR, 0, f"Video unavailable: {error_type}")
                    return False
                
            except Exception as e:
                if attempt < config.MAX_RETRIES - 1:
                    delay = config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt)
                    if progress_callback:
                        progress_callback(
                            config.PROGRESS_DOWNLOAD, 
                            20 + (attempt * 10), 
                            f"Retry in {delay}s..."
                        )
                    time.sleep(delay)
                else:
                    # Last attempt failed, try next strategy
                    break
    
    # All strategies failed
    if progress_callback:
        progress_callback(config.PROGRESS_ERROR, 0, "All download strategies failed")
    return False


def _download_with_strategy(
    video_id: str,
    start: float,
    end: float,
    output_file: str,
    strategy: str,
    progress_callback: Optional[Callable] = None
) -> Tuple[bool, str]:
    """
    Download using a specific strategy.
    
    Returns:
        Tuple of (success: bool, error_type: str)
    """
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--force-ipv4",
        "--no-warnings",
        "--remote-components", "ejs:github",
    ]
    
    # Apply strategy-specific options
    if strategy == "cookies_deno":
        cookies_path = Path(config.COOKIES_FILE)
        if cookies_path.exists():
            cmd.extend(["--cookies", str(cookies_path)])
        # Check if deno is available
        if Path(config.DENO_PATH).exists():
            cmd.extend(["--exec", f"deno:{config.DENO_PATH}"])
    
    elif strategy == "cookies_only":
        cookies_path = Path(config.COOKIES_FILE)
        if cookies_path.exists():
            cmd.extend(["--cookies", str(cookies_path)])
    
    elif strategy == "no_cookies":
        # No cookies, just try direct
        pass
    
    elif strategy == "tv_client":
        # Use TV client extractor (sometimes bypasses bot detection)
        cmd.extend(["--extractor-args", "youtube:player_client=tv"])
    
    # Add download options
    cmd.extend([
        "--downloader", "ffmpeg",
        "--downloader-args",
        f"ffmpeg_i:-ss {start} -to {end} -hide_banner -loglevel error",
        "-f",
        "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "-o", output_file,
        f"https://youtu.be/{video_id}"
    ])
    
    try:
        # Run with progress parsing
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Parse output for progress
        last_progress = 0
        stderr_output = []
        
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                stderr_output.append(line)
                
                # Parse download progress
                progress_match = re.search(r'(\d+\.?\d*)%', line)
                if progress_match and progress_callback:
                    progress = float(progress_match.group(1))
                    if progress > last_progress:
                        progress_callback(config.PROGRESS_DOWNLOAD, int(progress), "Downloading...")
                        last_progress = progress
        
        returncode = process.wait(timeout=300)
        stderr_text = ''.join(stderr_output)
        
        if returncode != 0:
            # Analyze error
            error_type = _analyze_error(stderr_text)
            return False, error_type
        
        # Check if file was created
        if not os.path.exists(output_file):
            return False, config.ERROR_UNKNOWN
        
        # Check if file has content
        if os.path.getsize(output_file) < 1024:  # Less than 1KB is suspicious
            return False, config.ERROR_UNKNOWN
        
        return True, ""
    
    except subprocess.TimeoutExpired:
        return False, config.ERROR_TIMEOUT
    except Exception as e:
        return False, config.ERROR_UNKNOWN


def _analyze_error(stderr: str) -> str:
    """
    Analyze error message to determine error type.
    
    Returns:
        Error type constant from config
    """
    stderr_lower = stderr.lower()
    
    # Bot detection / Sign in required
    if any(phrase in stderr_lower for phrase in [
        'sign in', 'bot', 'captcha', 'unable to extract', 
        'this video is unavailable', 'members-only'
    ]):
        return config.ERROR_BOT_DETECTION
    
    # Video not found
    if any(phrase in stderr_lower for phrase in [
        'video unavailable', 'not available', 'removed', 'deleted',
        'this video has been removed', 'video id'
    ]):
        return config.ERROR_NOT_FOUND
    
    # Private video
    if 'private' in stderr_lower:
        return config.ERROR_PRIVATE
    
    # Age restricted
    if 'age' in stderr_lower and 'restrict' in stderr_lower:
        return config.ERROR_AGE_RESTRICTED
    
    # Network errors
    if any(phrase in stderr_lower for phrase in [
        'network', 'connection', 'timeout', 'timed out', 'unreachable'
    ]):
        return config.ERROR_NETWORK
    
    return config.ERROR_UNKNOWN


def download_audio_only(
    video_id: str,
    output_file: str,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Download audio only for transcription.
    Uses same fallback strategies as video download.
    
    Args:
        video_id: YouTube video ID
        output_file: Path to save the audio file
        progress_callback: Optional callback function for progress updates
        
    Returns:
        True if successful, False otherwise
    """
    if progress_callback:
        progress_callback(config.PROGRESS_DOWNLOAD, 0, "Downloading audio for transcription")
    
    for strategy in config.YT_DOWNLOAD_STRATEGIES:
        for attempt in range(config.MAX_RETRIES):
            try:
                cmd = [
                    sys.executable, "-m", "yt_dlp",
                    "--force-ipv4",
                    "--no-warnings",
                    "--remote-components", "ejs:github",
                ]
                
                # Apply strategy
                if strategy == "cookies_deno":
                    cookies_path = Path(config.COOKIES_FILE)
                    if cookies_path.exists():
                        cmd.extend(["--cookies", str(cookies_path)])
                    if Path(config.DENO_PATH).exists():
                        cmd.extend(["--exec", f"deno:{config.DENO_PATH}"])
                
                elif strategy == "cookies_only":
                    cookies_path = Path(config.COOKIES_FILE)
                    if cookies_path.exists():
                        cmd.extend(["--cookies", str(cookies_path)])
                
                elif strategy == "tv_client":
                    cmd.extend(["--extractor-args", "youtube:player_client=tv"])
                
                # Audio-only format
                cmd.extend([
                    "-f", "bestaudio[ext=m4a]/bestaudio",
                    "-o", output_file,
                    f"https://youtu.be/{video_id}"
                ])
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0 and os.path.exists(output_file):
                    if progress_callback:
                        progress_callback(config.PROGRESS_DOWNLOAD, 100, "Audio download complete")
                    return True
                
                # Check for permanent errors
                error_type = _analyze_error(result.stderr)
                if error_type in [config.ERROR_NOT_FOUND, config.ERROR_PRIVATE, config.ERROR_AGE_RESTRICTED]:
                    return False
                
            except Exception:
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt))
                else:
                    break
    
    return False


def check_oauth_tokens() -> bool:
    """
    Check if OAuth2 tokens are available for yt-dlp.
    
    Returns:
        True if tokens found, False otherwise
    """
    oauth_cache = Path.home() / ".cache" / "yt-dlp" / "youtube-nsig"
    return oauth_cache.exists() and any(oauth_cache.iterdir())


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


def test_youtube_connectivity(video_id: str = "dQw4w9WgXcQ") -> dict:
    """
    Test YouTube connectivity and available strategies.
    
    Args:
        video_id: Test video ID (default: Rick Astley - Never Gonna Give You Up)
        
    Returns:
        Dict with test results for each strategy
    """
    results = {
        "oauth_available": check_oauth_tokens(),
        "cookies_available": Path(config.COOKIES_FILE).exists(),
        "deno_available": Path(config.DENO_PATH).exists(),
        "strategies": {}
    }
    
    for strategy in config.YT_DOWNLOAD_STRATEGIES:
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--force-ipv4",
                "--no-warnings",
                "--skip-download",
                "--remote-components", "ejs:github",
            ]
            
            if strategy == "cookies_deno" and results["cookies_available"]:
                cmd.extend(["--cookies", config.COOKIES_FILE])
            elif strategy == "cookies_only" and results["cookies_available"]:
                cmd.extend(["--cookies", config.COOKIES_FILE])
            elif strategy == "tv_client":
                cmd.extend(["--extractor-args", "youtube:player_client=tv"])
            
            cmd.append(f"https://youtu.be/{video_id}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            results["strategies"][strategy] = {
                "success": result.returncode == 0,
                "error": _analyze_error(result.stderr) if result.returncode != 0 else None
            }
        
        except Exception as e:
            results["strategies"][strategy] = {
                "success": False,
                "error": str(e)
            }
    
    return results
