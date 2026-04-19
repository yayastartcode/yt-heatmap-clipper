"""
Configuration file for YT Heatmap Clipper
Centralized settings for all modules
"""
import os

# Output settings
OUTPUT_DIR = "clips"
TEMP_DIR = "temp"

# Clip generation settings
MAX_DURATION = 60          # Maximum duration (seconds) for each clip
MIN_SCORE = 0.40          # Minimum heatmap intensity score
MAX_CLIPS = 10            # Maximum number of clips per video
PADDING = 10              # Extra seconds before/after segment

# Video processing settings
TOP_HEIGHT = 960          # Height for top section in split mode
BOTTOM_HEIGHT = 320       # Height for bottom section in split mode
VIDEO_WIDTH = 720         # Output video width
VIDEO_HEIGHT = 1280       # Output video height (9:16 aspect ratio)

# FFmpeg encoding settings
FFMPEG_PRESET = "ultrafast"
FFMPEG_CRF = 26
AUDIO_BITRATE = "128k"

# Subtitle settings
USE_SUBTITLE = True
WHISPER_MODEL = "small"   # tiny, base, small, medium, large
WHISPER_LANGUAGE = "id"   # Indonesian
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# Subtitle styling
SUBTITLE_FONT = "Arial"
SUBTITLE_FONTSIZE = 12
SUBTITLE_BOLD = 1
SUBTITLE_PRIMARY_COLOR = "&HFFFFFF"  # White
SUBTITLE_OUTLINE_COLOR = "&H000000"  # Black
SUBTITLE_OUTLINE = 2
SUBTITLE_SHADOW = 1
SUBTITLE_MARGIN_V = 100

# Parallel processing
PARALLEL_WORKERS = 4      # Number of concurrent clip processors
MAX_BATCH_SIZE = 10       # Maximum URLs in batch

# Thumbnail settings
THUMBNAIL_ENABLED = True
THUMBNAIL_FORMAT = "jpg"
THUMBNAIL_QUALITY = 85

# AI features
AI_TITLE_ENABLED = True
AI_DESCRIPTION_ENABLED = True
AUTO_DETECT_FACECAM = True

# Watermark settings
WATERMARK_ENABLED = False
WATERMARK_TEXT = ""
WATERMARK_POSITION = "bottom-right"  # top-left, top-right, bottom-left, bottom-right
WATERMARK_OPACITY = 0.7

# Background music
BGM_ENABLED = False
BGM_PATH = ""
BGM_VOLUME = 0.3

# Network settings
REQUEST_TIMEOUT = 20
USER_AGENT = "Mozilla/5.0"

# Cache settings
CACHE_DIR = os.path.expanduser("~/.cache/yt-heatmap-clipper")
MODEL_CACHE_DIR = os.path.expanduser("~/.cache/huggingface/hub")

# Crop modes
CROP_MODES = {
    "default": "Center crop (standard vertical video)",
    "split_left": "Split crop (top: center, bottom: bottom-left facecam)",
    "split_right": "Split crop (top: center, bottom: bottom-right facecam)"
}

# Progress callback types
PROGRESS_DOWNLOAD = "download"
PROGRESS_CROP = "crop"
PROGRESS_SUBTITLE = "subtitle"
PROGRESS_COMPLETE = "complete"
PROGRESS_ERROR = "error"
