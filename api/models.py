"""
Pydantic models for API request/response schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum


class CropMode(str, Enum):
    """Video crop modes"""
    NONE = "none"
    VERTICAL = "vertical"
    SQUARE = "square"
    FACECAM_LEFT = "facecam_left"
    FACECAM_RIGHT = "facecam_right"
    AUTO = "auto"


class ClipMode(str, Enum):
    """Clip detection modes"""
    HEATMAP = "heatmap"
    TRANSCRIPT = "transcript"
    MANUAL = "manual"
    EVEN_SPLIT = "even_split"


class WhisperModel(str, Enum):
    """Whisper model sizes"""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class JobStatus(str, Enum):
    """Job processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ManualSegment(BaseModel):
    """Manual timestamp segment"""
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")


class JobRequest(BaseModel):
    """Request to process a video"""
    url: str = Field(..., description="YouTube video URL")
    clip_mode: ClipMode = Field(default=ClipMode.HEATMAP, description="Clip detection mode")
    crop_mode: CropMode = Field(default=CropMode.NONE, description="Video crop mode")
    use_subtitle: bool = Field(default=True, description="Generate subtitles")
    whisper_model: WhisperModel = Field(default=WhisperModel.SMALL, description="Whisper model size")
    whisper_language: str = Field(default="id", description="Subtitle language code")
    max_clips: int = Field(default=10, description="Maximum clips to generate")
    min_score: float = Field(default=0.40, description="Minimum heatmap score")
    manual_segments: Optional[List[ManualSegment]] = Field(default=None, description="Manual timestamp segments")
    split_count: Optional[int] = Field(default=5, description="Number of clips for even_split mode")


class BatchJobRequest(BaseModel):
    """Request to process multiple videos"""
    urls: List[str] = Field(..., description="List of YouTube URLs")
    clip_mode: ClipMode = Field(default=ClipMode.HEATMAP)
    crop_mode: CropMode = Field(default=CropMode.NONE)
    use_subtitle: bool = Field(default=True)
    whisper_model: WhisperModel = Field(default=WhisperModel.SMALL)
    whisper_language: str = Field(default="id")
    max_clips: int = Field(default=10)
    min_score: float = Field(default=0.40)
    manual_segments: Optional[List[ManualSegment]] = Field(default=None)
    split_count: Optional[int] = Field(default=5)


class ClipInfo(BaseModel):
    """Information about a generated clip"""
    filename: str
    thumbnail: Optional[str] = None
    duration: float
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: float
    end_time: float
    score: float


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: JobStatus
    progress: float = Field(default=0.0, ge=0.0)
    clips_done: int = Field(default=0)
    total_clips: int = Field(default=0)
    current_stage: Optional[str] = None
    error: Optional[str] = None
    created_at: float
    updated_at: float


class JobClipsResponse(BaseModel):
    """List of clips for a job"""
    job_id: str
    clips: List[ClipInfo]
    total: int


class JobCreateResponse(BaseModel):
    """Response when creating a new job"""
    job_id: str
    status: JobStatus
    message: str


class ProgressMessage(BaseModel):
    """WebSocket progress message"""
    type: str = "progress"
    job_id: str
    clip: int
    total: int
    stage: str
    percent: float
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
