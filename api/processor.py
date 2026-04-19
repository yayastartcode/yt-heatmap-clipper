"""
Video processing logic that integrates with core modules
"""
import asyncio
import traceback
from pathlib import Path
from typing import Dict, Any

from api.job_manager import job_manager
from api.models import JobStatus

# These imports will work once Agent 1 completes the core modules
# For now, we create stub implementations that can be replaced
try:
    from core.heatmap import ambil_most_replayed
    from core.downloader import download_segment
    from core.processor import process_clip
    from core.subtitle import generate_subtitle
    from core.thumbnail import extract_thumbnail
    from core.detector import detect_facecam
    from core.ai import generate_title_description
    import config
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    print("⚠️  Core modules not yet available. Using stub implementation.")


async def process_video(job_id: str, job_data: Dict[str, Any]):
    """
    Process a video URL and generate clips
    
    This function:
    1. Updates job status to PROCESSING
    2. Calls core modules to extract heatmap and generate clips
    3. Updates progress via job_manager
    4. Handles errors and updates job status accordingly
    """
    try:
        # Update job status
        await job_manager.update_job(job_id, {
            "status": JobStatus.PROCESSING,
            "current_stage": "initializing",
            "progress": 0.0
        })
        
        if not CORE_AVAILABLE:
            # Stub implementation for testing
            await _stub_process_video(job_id, job_data)
            return
        
        # Extract parameters
        url = job_data["url"]
        crop_mode = job_data.get("crop_mode", "none")
        use_subtitle = job_data.get("use_subtitle", True)
        whisper_model = job_data.get("whisper_model", "small")
        whisper_language = job_data.get("whisper_language", "id")
        max_clips = job_data.get("max_clips", 10)
        min_score = job_data.get("min_score", 0.40)
        
        # Stage 1: Extract heatmap data
        await job_manager.update_job(job_id, {
            "current_stage": "extracting_heatmap",
            "progress": 10.0
        })
        
        heatmap_data = await asyncio.to_thread(
            ambil_most_replayed,
            url,
            max_clips=max_clips,
            min_score=min_score
        )
        
        if not heatmap_data:
            raise Exception("No heatmap data found for this video")
        
        total_clips = len(heatmap_data)
        await job_manager.update_job(job_id, {
            "total_clips": total_clips,
            "progress": 20.0
        })
        
        # Stage 2: Process each clip
        for idx, segment in enumerate(heatmap_data, 1):
            clip_progress = 20.0 + (70.0 * idx / total_clips)
            
            # Download segment
            await job_manager.update_job(job_id, {
                "current_stage": f"downloading_clip_{idx}",
                "progress": clip_progress
            })
            
            video_path = await asyncio.to_thread(
                download_segment,
                url,
                segment["start"],
                segment["end"]
            )
            
            # Process clip (crop, etc.)
            await job_manager.update_job(job_id, {
                "current_stage": f"processing_clip_{idx}",
                "progress": clip_progress + 10
            })
            
            output_path = await asyncio.to_thread(
                process_clip,
                video_path,
                crop_mode=crop_mode,
                output_dir="clips"
            )
            
            # Generate subtitle if requested
            if use_subtitle:
                await job_manager.update_job(job_id, {
                    "current_stage": f"generating_subtitle_{idx}",
                    "progress": clip_progress + 20
                })
                
                await asyncio.to_thread(
                    generate_subtitle,
                    output_path,
                    model=whisper_model,
                    language=whisper_language
                )
            
            # Extract thumbnail
            thumbnail_path = await asyncio.to_thread(
                extract_thumbnail,
                output_path
            )
            
            # Generate AI title/description (optional)
            title = None
            description = None
            try:
                title, description = await asyncio.to_thread(
                    generate_title_description,
                    output_path
                )
            except Exception as e:
                print(f"AI title generation failed: {e}")
            
            # Add clip to job
            clip_info = {
                "filename": Path(output_path).name,
                "thumbnail": Path(thumbnail_path).name if thumbnail_path else None,
                "duration": segment["end"] - segment["start"],
                "title": title,
                "description": description,
                "start_time": segment["start"],
                "end_time": segment["end"],
                "score": segment["score"]
            }
            
            await job_manager.add_clip(job_id, clip_info)
        
        # Stage 3: Complete
        await job_manager.update_job(job_id, {
            "status": JobStatus.COMPLETED,
            "current_stage": "completed",
            "progress": 100.0
        })
    
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error processing job {job_id}: {error_msg}")
        
        await job_manager.update_job(job_id, {
            "status": JobStatus.FAILED,
            "error": str(e),
            "progress": 0.0
        })


async def _stub_process_video(job_id: str, job_data: Dict[str, Any]):
    """
    Stub implementation for testing without core modules
    """
    # Simulate processing stages
    stages = [
        ("extracting_heatmap", 20),
        ("downloading_clip_1", 40),
        ("processing_clip_1", 60),
        ("generating_subtitle_1", 80),
        ("completed", 100)
    ]
    
    await job_manager.update_job(job_id, {
        "total_clips": 1
    })
    
    for stage, progress in stages:
        await asyncio.sleep(2)  # Simulate work
        
        await job_manager.update_job(job_id, {
            "current_stage": stage,
            "progress": float(progress)
        })
    
    # Add a dummy clip
    await job_manager.add_clip(job_id, {
        "filename": "test_clip.mp4",
        "thumbnail": "test_thumb.jpg",
        "duration": 30.0,
        "title": "Test Clip",
        "description": "This is a test clip",
        "start_time": 0.0,
        "end_time": 30.0,
        "score": 0.85
    })
    
    await job_manager.update_job(job_id, {
        "status": JobStatus.COMPLETED
    })
