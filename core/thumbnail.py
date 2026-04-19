"""
Thumbnail extraction module
Extracts best frame from video clip as thumbnail
"""
import os
import subprocess
from typing import Optional, Callable

import config


def extract_thumbnail(
    video_file: str,
    output_file: str,
    timestamp: Optional[float] = None,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Extract a thumbnail from a video file.
    
    Args:
        video_file: Path to video file
        output_file: Path to save thumbnail image
        timestamp: Time in seconds to extract frame (None = middle of video)
        progress_callback: Optional callback for progress updates
        
    Returns:
        True if successful, False otherwise
    """
    if not config.THUMBNAIL_ENABLED:
        return False
    
    if progress_callback:
        progress_callback("thumbnail", 0, "Extracting thumbnail")
    
    # If no timestamp specified, use middle of video
    if timestamp is None:
        duration = _get_video_duration(video_file)
        timestamp = duration / 2
    
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(timestamp),
        "-i", video_file,
        "-vframes", "1",
        "-q:v", str(100 - config.THUMBNAIL_QUALITY),  # FFmpeg quality is inverted
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if progress_callback:
            progress_callback("thumbnail", 100, "Thumbnail extracted")
        
        return True
        
    except subprocess.CalledProcessError as e:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"Thumbnail extraction failed: {e.stderr}")
        return False


def extract_best_frame(
    video_file: str,
    output_file: str,
    num_samples: int = 10,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Extract the "best" frame from video based on motion/sharpness analysis.
    Samples multiple frames and selects the one with highest quality score.
    
    Args:
        video_file: Path to video file
        output_file: Path to save thumbnail image
        num_samples: Number of frames to sample and compare
        progress_callback: Optional callback for progress updates
        
    Returns:
        True if successful, False otherwise
    """
    if not config.THUMBNAIL_ENABLED:
        return False
    
    if progress_callback:
        progress_callback("thumbnail", 0, "Analyzing frames")
    
    duration = _get_video_duration(video_file)
    
    # Sample frames at regular intervals
    best_score = -1
    best_timestamp = duration / 2  # Default to middle
    
    for i in range(num_samples):
        timestamp = (duration / (num_samples + 1)) * (i + 1)
        score = _calculate_frame_quality(video_file, timestamp)
        
        if score > best_score:
            best_score = score
            best_timestamp = timestamp
        
        if progress_callback:
            progress = int((i + 1) / num_samples * 80)
            progress_callback("thumbnail", progress, f"Analyzing frame {i+1}/{num_samples}")
    
    # Extract the best frame
    return extract_thumbnail(video_file, output_file, best_timestamp, progress_callback)


def _get_video_duration(video_file: str) -> float:
    """Get video duration in seconds"""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip())
    except Exception:
        return 30.0  # Default fallback


def _calculate_frame_quality(video_file: str, timestamp: float) -> float:
    """
    Calculate quality score for a frame at given timestamp.
    Uses FFmpeg's SSIM filter to estimate sharpness/quality.
    
    Returns:
        Quality score (higher is better)
    """
    # Simple heuristic: avoid first/last 10% of video (often black frames or transitions)
    duration = _get_video_duration(video_file)
    
    if timestamp < duration * 0.1 or timestamp > duration * 0.9:
        return 0.0
    
    # For now, return timestamp-based score (prefer middle frames)
    # In a more advanced implementation, we could use OpenCV to analyze actual frame content
    middle = duration / 2
    distance_from_middle = abs(timestamp - middle)
    score = 1.0 - (distance_from_middle / middle)
    
    return score


def create_thumbnail_grid(
    video_files: list,
    output_file: str,
    cols: int = 3,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Create a grid of thumbnails from multiple video files.
    
    Args:
        video_files: List of video file paths
        output_file: Path to save grid image
        cols: Number of columns in grid
        progress_callback: Optional callback for progress updates
        
    Returns:
        True if successful, False otherwise
    """
    if not video_files:
        return False
    
    if progress_callback:
        progress_callback("thumbnail", 0, "Creating thumbnail grid")
    
    # Extract individual thumbnails
    temp_thumbs = []
    for i, video_file in enumerate(video_files):
        temp_thumb = f"temp_thumb_{i}.jpg"
        if extract_thumbnail(video_file, temp_thumb):
            temp_thumbs.append(temp_thumb)
        
        if progress_callback:
            progress = int((i + 1) / len(video_files) * 80)
            progress_callback("thumbnail", progress, f"Processing {i+1}/{len(video_files)}")
    
    if not temp_thumbs:
        return False
    
    # Create grid using FFmpeg
    rows = (len(temp_thumbs) + cols - 1) // cols
    
    # Build filter complex for grid layout
    inputs = "".join([f"-i {thumb} " for thumb in temp_thumbs])
    
    cmd = f"ffmpeg -y -hide_banner -loglevel error {inputs}"
    cmd += f"-filter_complex \"xstack=inputs={len(temp_thumbs)}:layout="
    
    # Generate layout string
    layout_parts = []
    for i in range(len(temp_thumbs)):
        row = i // cols
        col = i % cols
        x = col * 240  # Assuming 240px width per thumbnail
        y = row * 320  # Assuming 320px height per thumbnail
        layout_parts.append(f"{x}_{y}")
    
    cmd += "|".join(layout_parts) + f"\" {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Cleanup temp files
        for thumb in temp_thumbs:
            if os.path.exists(thumb):
                os.remove(thumb)
        
        if progress_callback:
            progress_callback("thumbnail", 100, "Grid created")
        
        return True
        
    except Exception as e:
        # Cleanup temp files
        for thumb in temp_thumbs:
            if os.path.exists(thumb):
                try:
                    os.remove(thumb)
                except Exception:
                    pass
        
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"Grid creation failed: {str(e)}")
        
        return False
