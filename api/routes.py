"""
API routes for video processing
"""
import asyncio
import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from api.models import (
    JobRequest, BatchJobRequest, JobCreateResponse, 
    JobStatusResponse, JobClipsResponse, JobStatus, ClipInfo
)
from api.job_manager import job_manager
from api.processor import process_video


router = APIRouter()


@router.post("/process", response_model=JobCreateResponse)
async def process_video_endpoint(
    request: JobRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a video URL for processing
    """
    try:
        # Create job
        job_data = request.model_dump()
        job_id = await job_manager.create_job(job_data)
        
        # Start processing in background
        background_tasks.add_task(process_video, job_id, job_data)
        
        return JobCreateResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            message="Job created successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=List[JobCreateResponse])
async def batch_process_endpoint(
    request: BatchJobRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit multiple video URLs for batch processing
    """
    try:
        responses = []
        
        for url in request.urls:
            # Create individual job for each URL
            job_data = {
                "url": url,
                "crop_mode": request.crop_mode,
                "use_subtitle": request.use_subtitle,
                "whisper_model": request.whisper_model,
                "whisper_language": request.whisper_language,
                "max_clips": request.max_clips,
                "min_score": request.min_score
            }
            
            job_id = await job_manager.create_job(job_data)
            
            # Start processing in background
            background_tasks.add_task(process_video, job_id, job_data)
            
            responses.append(JobCreateResponse(
                job_id=job_id,
                status=JobStatus.QUEUED,
                message=f"Job created for {url}"
            ))
        
        return responses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get job processing status
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        clips_done=job["clips_done"],
        total_clips=job["total_clips"],
        current_stage=job["current_stage"],
        error=job["error"],
        created_at=job["created_at"],
        updated_at=job["updated_at"]
    )


@router.get("/clips/{job_id}", response_model=JobClipsResponse)
async def get_job_clips(job_id: str):
    """
    Get list of generated clips for a job
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    clips = [ClipInfo(**clip) for clip in job.get("clips", [])]
    
    return JobClipsResponse(
        job_id=job_id,
        clips=clips,
        total=len(clips)
    )


@router.get("/download/{job_id}/{filename}")
async def download_clip(job_id: str, filename: str):
    """
    Download a specific clip file
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Security: ensure filename is in job's clips
    clip_filenames = [clip["filename"] for clip in job.get("clips", [])]
    if filename not in clip_filenames:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    file_path = Path("clips") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename
    )


@router.get("/thumbnail/{job_id}/{filename}")
async def get_thumbnail(job_id: str, filename: str):
    """
    Get thumbnail for a clip
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Find clip with matching filename
    clip = next((c for c in job.get("clips", []) if c["filename"] == filename), None)
    
    if not clip or not clip.get("thumbnail"):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    thumbnail_path = Path("clips") / clip["thumbnail"]
    
    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    
    return FileResponse(
        path=thumbnail_path,
        media_type="image/jpeg"
    )


@router.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its associated files
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete clip files
    for clip in job.get("clips", []):
        clip_path = Path("clips") / clip["filename"]
        if clip_path.exists():
            clip_path.unlink()
        
        if clip.get("thumbnail"):
            thumb_path = Path("clips") / clip["thumbnail"]
            if thumb_path.exists():
                thumb_path.unlink()
    
    # Delete job file
    job_file = Path("jobs") / f"{job_id}.json"
    if job_file.exists():
        job_file.unlink()
    
    # Remove from memory
    if job_id in job_manager.jobs:
        del job_manager.jobs[job_id]
    
    return {"message": "Job deleted successfully"}
