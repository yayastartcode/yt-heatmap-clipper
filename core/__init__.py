"""
Core package for YT Heatmap Clipper
Contains modular components for video processing
"""

from .heatmap import extract_heatmap_data, get_video_duration, extract_video_id
from .downloader import download_video_segment
from .processor import process_clip, CropMode
from .subtitle import generate_subtitle, format_timestamp
from .thumbnail import extract_thumbnail
from .detector import detect_facecam_position, suggest_crop_mode
from .ai import generate_title, generate_description

__all__ = [
    'extract_video_id',
    'extract_heatmap_data',
    'get_video_duration',
    'download_video_segment',
    'process_clip',
    'CropMode',
    'generate_subtitle',
    'format_timestamp',
    'extract_thumbnail',
    'detect_facecam_position',
    'suggest_crop_mode',
    'generate_title',
    'generate_description'
]
