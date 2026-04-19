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
import config
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
                "clip_mode": request.clip_mode,
                "crop_mode": request.crop_mode,
                "use_subtitle": request.use_subtitle,
                "whisper_model": request.whisper_model,
                "whisper_language": request.whisper_language,
                "max_clips": request.max_clips,
                "min_score": request.min_score,
                "manual_segments": request.manual_segments,
                "split_count": request.split_count
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
        progress=min(job["progress"], 100.0),
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


@router.post("/cancel/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a running job
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] not in ["queued", "processing"]:
        raise HTTPException(status_code=400, detail="Job is not running")
    
    # Update job status
    job["status"] = "cancelled"
    job["error"] = "Cancelled by user"
    await job_manager.update_job(job_id, job)
    
    # TODO: Actually kill the process if it's running
    # This would require tracking process IDs
    
    return {"message": "Job cancelled"}


@router.post("/retry/{job_id}")
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks
):
    """
    Retry a failed job
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] not in ["failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Job is not failed or cancelled")
    
    # Reset job status
    job["status"] = "queued"
    job["progress"] = 0
    job["error"] = None
    job["clips_done"] = 0
    job["current_stage"] = "Queued"
    await job_manager.update_job(job_id, job)
    
    # Restart processing
    job_data = {
        "url": job.get("url"),
        "clip_mode": job.get("clip_mode"),
        "crop_mode": job.get("crop_mode"),
        "use_subtitle": job.get("use_subtitle"),
        "whisper_model": job.get("whisper_model"),
        "whisper_language": job.get("whisper_language"),
        "max_clips": job.get("max_clips"),
        "min_score": job.get("min_score"),
        "manual_segments": job.get("manual_segments"),
        "split_count": job.get("split_count")
    }
    
    background_tasks.add_task(process_video, job_id, job_data)
    
    return {"message": "Job restarted", "job_id": job_id}


@router.get("/download-all/{job_id}")
async def download_all_clips(job_id: str):
    """
    Download all clips as a ZIP file
    """
    import zipfile
    import tempfile
    
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    clips = job.get("clips", [])
    if not clips:
        raise HTTPException(status_code=404, detail="No clips found")
    
    # Create temporary ZIP file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.zip') as tmp_file:
        zip_path = tmp_file.name
        
        with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for clip in clips:
                clip_path = Path("clips") / clip["filename"]
                if clip_path.exists():
                    zipf.write(clip_path, clip["filename"])
                
                # Also include thumbnail if available
                if clip.get("thumbnail"):
                    thumb_path = Path("clips") / clip["thumbnail"]
                    if thumb_path.exists():
                        zipf.write(thumb_path, clip["thumbnail"])
    
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"{job_id}_clips.zip",
        background=lambda: os.unlink(zip_path)  # Clean up after sending
    )


@router.post("/upload-cookies")
async def upload_cookies(file: bytes):
    """
    Upload cookies.txt file for yt-dlp
    """
    try:
        # Save cookies file
        cookies_path = Path(config.COOKIES_FILE)
        cookies_path.write_bytes(file)
        
        return {
            "message": "Cookies uploaded successfully",
            "path": str(cookies_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload cookies: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint with system information
    """
    import shutil
    import subprocess
    
    # Check disk space
    clips_dir = Path("clips")
    if clips_dir.exists():
        total, used, free = shutil.disk_usage(clips_dir)
        disk_info = {
            "total_gb": total / (1024**3),
            "used_gb": used / (1024**3),
            "free_gb": free / (1024**3)
        }
    else:
        disk_info = {"error": "Clips directory not found"}
    
    # Check ffmpeg version
    try:
        ffmpeg_result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        ffmpeg_version = ffmpeg_result.stdout.split('\n')[0] if ffmpeg_result.returncode == 0 else "Not found"
    except Exception:
        ffmpeg_version = "Not found"
    
    # Check Whisper model status
    whisper_status = "Not checked"
    try:
        from faster_whisper import WhisperModel
        whisper_status = f"Available (model: {config.WHISPER_MODEL})"
    except ImportError:
        whisper_status = "Not installed"
    except Exception as e:
        whisper_status = f"Error: {str(e)}"
    
    # Check yt-dlp
    try:
        ytdlp_result = subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        ytdlp_version = ytdlp_result.stdout.strip() if ytdlp_result.returncode == 0 else "Not found"
    except Exception:
        ytdlp_version = "Not found"
    
    # Job statistics
    jobs = list(job_manager.jobs.values())
    job_stats = {
        "total": len(jobs),
        "queued": len([j for j in jobs if j["status"] == "queued"]),
        "processing": len([j for j in jobs if j["status"] == "processing"]),
        "completed": len([j for j in jobs if j["status"] == "completed"]),
        "failed": len([j for j in jobs if j["status"] == "failed"])
    }
    
    return {
        "status": "healthy",
        "disk": disk_info,
        "ffmpeg": ffmpeg_version,
        "whisper": whisper_status,
        "ytdlp": ytdlp_version,
        "jobs": job_stats,
        "config": {
            "llm_configured": bool(config.LLM_API_URL and config.LLM_API_KEY),
            "cookies_available": Path(config.COOKIES_FILE).exists(),
            "deno_available": Path(config.DENO_PATH).exists()
        }
    }
