"""
Video processor module
Handles FFmpeg video processing, cropping, and effects
"""
import os
import subprocess
from enum import Enum
from typing import Optional, Callable

import config


class CropMode(Enum):
    """Video crop modes"""
    DEFAULT = "default"
    SPLIT_LEFT = "split_left"
    SPLIT_RIGHT = "split_right"


def process_clip(
    input_file: str,
    output_file: str,
    crop_mode: CropMode = CropMode.DEFAULT,
    subtitle_file: Optional[str] = None,
    watermark_text: Optional[str] = None,
    bgm_file: Optional[str] = None,
    quality_preset: str = "balanced",
    resolution: str = "720p",
    output_format: str = "mp4",
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Process video clip with cropping, subtitle, watermark, and BGM.
    
    Args:
        input_file: Path to input video
        output_file: Path to output video
        crop_mode: Crop mode (default, split_left, split_right)
        subtitle_file: Optional path to SRT subtitle file
        watermark_text: Optional watermark text
        bgm_file: Optional background music file
        quality_preset: Quality preset (fast, balanced, quality)
        resolution: Resolution preset (720p, 1080p)
        output_format: Output format (mp4, webm)
        progress_callback: Optional callback for progress updates
        
    Returns:
        True if successful, False otherwise
    """
    if progress_callback:
        progress_callback(config.PROGRESS_CROP, 0, "Processing video")
    
    temp_cropped = input_file.replace(".mp4", "_cropped.mp4")
    
    # Get quality and resolution settings
    quality_settings = config.QUALITY_PRESETS.get(quality_preset, config.QUALITY_PRESETS["balanced"])
    resolution_settings = config.RESOLUTION_PRESETS.get(resolution, config.RESOLUTION_PRESETS["720p"])
    
    # Step 1: Crop video
    if not _crop_video(input_file, temp_cropped, crop_mode, quality_settings, resolution_settings, progress_callback):
        return False
    
    # Step 2: Add subtitle if provided
    if subtitle_file and os.path.exists(subtitle_file):
        temp_subtitled = temp_cropped.replace(".mp4", "_sub.mp4")
        if not _add_subtitle(temp_cropped, temp_subtitled, subtitle_file, quality_settings, resolution_settings, progress_callback):
            _cleanup_temp_files([temp_cropped])
            return False
        os.remove(temp_cropped)
        temp_cropped = temp_subtitled
    
    # Step 3: Add watermark if provided
    if watermark_text and config.WATERMARK_ENABLED:
        temp_watermarked = temp_cropped.replace(".mp4", "_wm.mp4")
        if not _add_watermark(temp_cropped, temp_watermarked, watermark_text, progress_callback):
            _cleanup_temp_files([temp_cropped])
            return False
        os.remove(temp_cropped)
        temp_cropped = temp_watermarked
    
    # Step 4: Add background music if provided
    if bgm_file and config.BGM_ENABLED and os.path.exists(bgm_file):
        if not _add_bgm(temp_cropped, output_file, bgm_file, progress_callback):
            _cleanup_temp_files([temp_cropped])
            return False
        os.remove(temp_cropped)
    else:
        # No BGM, just rename
        os.rename(temp_cropped, output_file)
    
    if progress_callback:
        progress_callback(config.PROGRESS_CROP, 100, "Video processing complete")
    
    return True


def _crop_video(
    input_file: str,
    output_file: str,
    crop_mode: CropMode,
    quality_settings: dict,
    resolution_settings: dict,
    progress_callback: Optional[Callable] = None
) -> bool:
    """Crop video based on crop mode with quality and resolution settings"""
    
    video_width = resolution_settings["width"]
    video_height = resolution_settings["height"]
    preset = quality_settings["preset"]
    crf = quality_settings["crf"]
    
    if crop_mode == CropMode.DEFAULT:
        # Standard center crop
        vf = f"scale=-2:{video_height},crop={video_width}:{video_height}:(iw-{video_width})/2:(ih-{video_height})/2"
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", input_file,
            "-vf", vf,
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-c:a", "aac", "-b:a", config.AUDIO_BITRATE,
            output_file
        ]
    
    elif crop_mode == CropMode.SPLIT_LEFT:
        # Split crop: top center + bottom left
        top_height = int(video_height * 0.75)
        bottom_height = video_height - top_height
        vf = (
            f"scale=-2:{video_height}[scaled];"
            f"[scaled]split=2[s1][s2];"
            f"[s1]crop={video_width}:{top_height}:(iw-{video_width})/2:(ih-{video_height})/2[top];"
            f"[s2]crop={video_width}:{bottom_height}:0:ih-{bottom_height}[bottom];"
            f"[top][bottom]vstack=inputs=2[out]"
        )
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", input_file,
            "-filter_complex", vf,
            "-map", "[out]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-c:a", "aac", "-b:a", config.AUDIO_BITRATE,
            output_file
        ]
    
    elif crop_mode == CropMode.SPLIT_RIGHT:
        # Split crop: top center + bottom right
        top_height = int(video_height * 0.75)
        bottom_height = video_height - top_height
        vf = (
            f"scale=-2:{video_height}[scaled];"
            f"[scaled]split=2[s1][s2];"
            f"[s1]crop={video_width}:{top_height}:(iw-{video_width})/2:(ih-{video_height})/2[top];"
            f"[s2]crop={video_width}:{bottom_height}:iw-{video_width}:ih-{bottom_height}[bottom];"
            f"[top][bottom]vstack=inputs=2[out]"
        )
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", input_file,
            "-filter_complex", vf,
            "-map", "[out]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-c:a", "aac", "-b:a", config.AUDIO_BITRATE,
            output_file
        ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except subprocess.CalledProcessError as e:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"Crop failed: {e.stderr}")
        return False


def _add_subtitle(
    input_file: str,
    output_file: str,
    subtitle_file: str,
    quality_settings: dict,
    resolution_settings: dict,
    progress_callback: Optional[Callable] = None
) -> bool:
    """Burn subtitle into video with improved styling"""
    
    preset = quality_settings["preset"]
    crf = quality_settings["crf"]
    video_width = resolution_settings["width"]
    
    # Scale font size based on resolution
    font_size = 18 if video_width >= 1080 else 14
    
    # Get absolute path and escape for FFmpeg
    abs_subtitle_path = os.path.abspath(subtitle_file)
    subtitle_path = abs_subtitle_path.replace("\\", "/").replace(":", "\\:")
    
    # Improved subtitle styling - larger, more readable
    force_style = (
        f"FontName={config.SUBTITLE_FONT},"
        f"FontSize={font_size},"
        f"Bold={config.SUBTITLE_BOLD},"
        f"PrimaryColour={config.SUBTITLE_PRIMARY_COLOR},"
        f"OutlineColour={config.SUBTITLE_OUTLINE_COLOR},"
        f"BorderStyle=3,"  # Box background
        f"Outline=3,"  # Thicker outline
        f"Shadow=2,"
        f"MarginV={config.SUBTITLE_MARGIN_V},"
        f"Alignment=2"  # Bottom center
    )
    
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_file,
        "-vf", f"subtitles='{subtitle_path}':force_style='{force_style}'",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-c:a", "copy",
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except subprocess.CalledProcessError as e:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"Subtitle failed: {e.stderr}")
        return False


def _add_watermark(
    input_file: str,
    output_file: str,
    watermark_text: str,
    progress_callback: Optional[Callable] = None
) -> bool:
    """Add text watermark to video"""
    
    # Position mapping
    positions = {
        "top-left": "x=10:y=10",
        "top-right": "x=w-tw-10:y=10",
        "bottom-left": "x=10:y=h-th-10",
        "bottom-right": "x=w-tw-10:y=h-th-10"
    }
    
    pos = positions.get(config.WATERMARK_POSITION, positions["bottom-right"])
    
    drawtext = (
        f"drawtext=text='{watermark_text}':"
        f"fontsize=24:fontcolor=white@{config.WATERMARK_OPACITY}:"
        f"borderw=2:bordercolor=black@{config.WATERMARK_OPACITY}:"
        f"{pos}"
    )
    
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_file,
        "-vf", drawtext,
        "-c:v", "libx264", "-preset", config.FFMPEG_PRESET, "-crf", str(config.FFMPEG_CRF),
        "-c:a", "copy",
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except subprocess.CalledProcessError as e:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"Watermark failed: {e.stderr}")
        return False


def _add_bgm(
    input_file: str,
    output_file: str,
    bgm_file: str,
    progress_callback: Optional[Callable] = None
) -> bool:
    """Add background music to video"""
    
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_file,
        "-i", bgm_file,
        "-filter_complex",
        f"[1:a]volume={config.BGM_VOLUME}[bgm];[0:a][bgm]amix=inputs=2:duration=shortest[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", config.AUDIO_BITRATE,
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except subprocess.CalledProcessError as e:
        if progress_callback:
            progress_callback(config.PROGRESS_ERROR, 0, f"BGM failed: {e.stderr}")
        return False


def _cleanup_temp_files(files: list):
    """Clean up temporary files"""
    for f in files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass
