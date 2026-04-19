"""
Subtitle generation module
Handles subtitle generation using Faster-Whisper
"""
import os
from typing import Optional, Callable

import config


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_subtitle(
    video_file: str,
    subtitle_file: str,
    model: str = None,
    language: str = None,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Generate subtitle file using Faster-Whisper for the given video.
    
    Args:
        video_file: Path to video file
        subtitle_file: Path to save subtitle file (.srt)
        model: Whisper model size (defaults to config.WHISPER_MODEL)
        language: Language code (defaults to config.WHISPER_LANGUAGE)
        progress_callback: Optional callback for progress updates
        
    Returns:
        True if successful, False otherwise
    """
    if model is None:
        model = config.WHISPER_MODEL
    if language is None:
        language = config.WHISPER_LANGUAGE
    
    try:
        from faster_whisper import WhisperModel
        
        if progress_callback:
            progress_callback(config.PROGRESS_SUBTITLE, 0, f"Loading Whisper model '{model}'")
        
        # Load model
        whisper_model = WhisperModel(
            model,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE
        )
        
        if progress_callback:
            progress_callback(config.PROGRESS_SUBTITLE, 30, "Transcribing audio")
        
        # Transcribe
        segments, info = whisper_model.transcribe(video_file, language=language)
        
        if progress_callback:
            progress_callback(config.PROGRESS_SUBTITLE, 80, "Generating subtitle file")
        
        # Generate SRT format
        with open(subtitle_file, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start_time = format_timestamp(segment.start)
                end_time = format_timestamp(segment.end)
                text = segment.text.strip()
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        if progress_callback:
            progress_callback(config.PROGRESS_SUBTITLE, 100, "Subtitle generation complete")
        
        return True
        
    except ImportError:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, "Faster-Whisper not installed")
        return False
    except Exception as e:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"Subtitle generation failed: {str(e)}")
        return False


def get_model_size(model: str) -> str:
    """
    Get the approximate size of a Whisper model.
    
    Args:
        model: Model name
        
    Returns:
        Size string (e.g., "466 MB")
    """
    sizes = {
        "tiny": "75 MB",
        "base": "142 MB",
        "small": "466 MB",
        "medium": "1.5 GB",
        "large-v1": "2.9 GB",
        "large-v2": "2.9 GB",
        "large-v3": "2.9 GB"
    }
    return sizes.get(model, "unknown size")


def check_whisper_installation() -> bool:
    """
    Check if Faster-Whisper is installed.
    
    Returns:
        True if installed, False otherwise
    """
    try:
        import faster_whisper
        return True
    except ImportError:
        return False


def install_whisper() -> bool:
    """
    Install Faster-Whisper package.
    
    Returns:
        True if successful, False otherwise
    """
    import subprocess
    import sys
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "faster-whisper"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120
        )
        return True
    except Exception:
        return False


def is_model_cached(model: str) -> bool:
    """
    Check if a Whisper model is already cached locally.
    
    Args:
        model: Model name
        
    Returns:
        True if cached, False otherwise
    """
    model_name = f"faster-whisper-{model}"
    
    if not os.path.exists(config.MODEL_CACHE_DIR):
        return False
    
    try:
        cached_items = os.listdir(config.MODEL_CACHE_DIR)
        return any(model_name in item.lower() for item in cached_items)
    except Exception:
        return False
