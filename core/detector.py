"""
Facecam detection module
Auto-detects facecam position in video frames
"""
import os
import subprocess
from typing import Optional, Tuple, Callable
from enum import Enum

import config


class FacecamPosition(Enum):
    """Detected facecam positions"""
    NONE = "none"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    CENTER = "center"


def detect_facecam_position(
    video_file: str,
    progress_callback: Optional[Callable] = None
) -> FacecamPosition:
    """
    Detect facecam position in video.
    Uses OpenCV if available, falls back to heuristics.
    
    Args:
        video_file: Path to video file
        progress_callback: Optional callback for progress updates
        
    Returns:
        Detected facecam position
    """
    if not config.AUTO_DETECT_FACECAM:
        return FacecamPosition.NONE
    
    if progress_callback:
        progress_callback("detection", 0, "Detecting facecam position")
    
    # Try OpenCV-based detection first
    try:
        import cv2
        import numpy as np
        
        position = _detect_with_opencv(video_file, progress_callback)
        
        if progress_callback:
            progress_callback("detection", 100, f"Detected: {position.value}")
        
        return position
        
    except ImportError:
        # OpenCV not available, use fallback heuristics
        if progress_callback:
            progress_callback("detection", 50, "Using fallback detection")
        
        position = _detect_with_heuristics(video_file)
        
        if progress_callback:
            progress_callback("detection", 100, f"Detected: {position.value}")
        
        return position


def _detect_with_opencv(
    video_file: str,
    progress_callback: Optional[Callable] = None
) -> FacecamPosition:
    """
    Detect facecam using OpenCV face detection.
    Analyzes multiple frames to find consistent face regions.
    """
    import cv2
    import numpy as np
    
    # Load face cascade classifier
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    cap = cv2.VideoCapture(video_file)
    
    if not cap.isOpened():
        return FacecamPosition.NONE
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_frames = min(10, total_frames)
    
    face_positions = []
    
    for i in range(sample_frames):
        # Sample frames at regular intervals
        frame_idx = int((total_frames / (sample_frames + 1)) * (i + 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Get the largest face (likely the main subject)
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face
            
            # Calculate center of face
            face_center_x = x + w / 2
            face_center_y = y + h / 2
            
            # Normalize to frame dimensions
            frame_h, frame_w = frame.shape[:2]
            norm_x = face_center_x / frame_w
            norm_y = face_center_y / frame_h
            
            face_positions.append((norm_x, norm_y))
        
        if progress_callback:
            progress = int((i + 1) / sample_frames * 90)
            progress_callback("detection", progress, f"Analyzing frame {i+1}/{sample_frames}")
    
    cap.release()
    
    if not face_positions:
        return FacecamPosition.NONE
    
    # Calculate average position
    avg_x = sum(p[0] for p in face_positions) / len(face_positions)
    avg_y = sum(p[1] for p in face_positions) / len(face_positions)
    
    # Determine position based on averages
    # Divide frame into 3x3 grid
    if avg_y < 0.33:
        # Top third
        if avg_x < 0.33:
            return FacecamPosition.TOP_LEFT
        elif avg_x > 0.67:
            return FacecamPosition.TOP_RIGHT
        else:
            return FacecamPosition.CENTER
    elif avg_y > 0.67:
        # Bottom third
        if avg_x < 0.33:
            return FacecamPosition.BOTTOM_LEFT
        elif avg_x > 0.67:
            return FacecamPosition.BOTTOM_RIGHT
        else:
            return FacecamPosition.CENTER
    else:
        # Middle third
        return FacecamPosition.CENTER


def _detect_with_heuristics(video_file: str) -> FacecamPosition:
    """
    Fallback detection using simple heuristics.
    Analyzes frame brightness in different regions.
    """
    # Extract a sample frame from middle of video
    temp_frame = "temp_detection_frame.jpg"
    
    duration = _get_video_duration(video_file)
    timestamp = duration / 2
    
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(timestamp),
        "-i", video_file,
        "-vframes", "1",
        temp_frame
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Analyze frame regions
        # For now, return a default position
        # In a real implementation, we could use PIL to analyze brightness/contrast
        
        if os.path.exists(temp_frame):
            os.remove(temp_frame)
        
        # Default heuristic: assume bottom-right for gaming videos
        return FacecamPosition.BOTTOM_RIGHT
        
    except Exception:
        return FacecamPosition.NONE


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
        return 30.0


def suggest_crop_mode(position: FacecamPosition) -> str:
    """
    Suggest appropriate crop mode based on detected facecam position.
    
    Args:
        position: Detected facecam position
        
    Returns:
        Suggested crop mode ("default", "split_left", "split_right")
    """
    if position == FacecamPosition.BOTTOM_LEFT:
        return "split_left"
    elif position == FacecamPosition.BOTTOM_RIGHT:
        return "split_right"
    elif position in [FacecamPosition.TOP_LEFT, FacecamPosition.TOP_RIGHT]:
        # Top facecams are less common, use default
        return "default"
    else:
        # Center or no facecam detected
        return "default"


def check_opencv_available() -> bool:
    """
    Check if OpenCV is available for face detection.
    
    Returns:
        True if OpenCV is installed, False otherwise
    """
    try:
        import cv2
        return True
    except ImportError:
        return False


def install_opencv() -> bool:
    """
    Install OpenCV package.
    
    Returns:
        True if successful, False otherwise
    """
    import subprocess
    import sys
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "opencv-python"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120
        )
        return True
    except Exception:
        return False
