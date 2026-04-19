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
    from core.heatmap import extract_video_id, extract_heatmap_data, get_video_duration
    from core.downloader import download_video_segment
    from core.processor import process_clip
    from core.subtitle import generate_subtitle
    from core.thumbnail import extract_thumbnail
    from core.detector import detect_facecam_position, suggest_crop_mode
    from core.ai import generate_title, generate_description
    import config
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    print(f"⚠️  Core modules not available: {e}. Using stub implementation.")


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
        crop_mode = job_data.get("crop_mode", "default")
        use_subtitle = job_data.get("use_subtitle", True)
        whisper_model = job_data.get("whisper_model", "small")
        whisper_language = job_data.get("whisper_language", "id")
        max_clips = job_data.get("max_clips", 10)
        min_score = job_data.get("min_score", 0.40)
        
        # Stage 1: Extract video ID and heatmap data
        await job_manager.update_job(job_id, {
            "current_stage": "extracting_heatmap",
            "progress": 10.0
        })
        
        video_id = extract_video_id(url)
        if not video_id:
            raise Exception("Invalid YouTube URL")
        
        heatmap_data = await asyncio.to_thread(
            extract_heatmap_data,
            video_id,
            min_score
        )
        
        if not heatmap_data:
            raise Exception("No heatmap data found for this video")
        
        # Limit clips
        heatmap_data = heatmap_data[:max_clips]
        total_clips = len(heatmap_data)
        
        total_duration = await asyncio.to_thread(get_video_duration, video_id)
        
        await job_manager.update_job(job_id, {
            "total_clips": total_clips,
            "progress": 20.0
        })
        
        import os
        os.makedirs("clips", exist_ok=True)
        os.makedirs("temp", exist_ok=True)
        
        # Map API crop_mode to core CropMode enum
        from core.processor import CropMode
        crop_mode_map = {
            "none": CropMode.DEFAULT,
            "default": CropMode.DEFAULT,
            "facecam_left": CropMode.SPLIT_LEFT,
            "facecam_right": CropMode.SPLIT_RIGHT,
            "vertical": CropMode.DEFAULT,
            "auto": CropMode.DEFAULT,
        }
        core_crop_mode = crop_mode_map.get(crop_mode, CropMode.DEFAULT)
        
        # Stage 2: Process each clip
        for idx, segment in enumerate(heatmap_data, 1):
            clip_progress = 20.0 + (70.0 * idx / total_clips)
            
            start = max(0, segment["start"] - config.PADDING)
            end = min(segment["start"] + segment["duration"] + config.PADDING, total_duration)
            
            if end - start < 3:
                continue
            
            temp_file = f"temp/temp_{job_id}_{idx}.mp4"
            cropped_file = os.path.join("clips", f"{job_id}_clip_{idx}.mp4")
            
            # Download segment
            await job_manager.update_job(job_id, {
                "current_stage": f"downloading_clip_{idx}",
                "progress": clip_progress
            })
            
            dl_success = await asyncio.to_thread(
                download_video_segment,
                video_id,
                start,
                end,
                temp_file
            )
            
            if not dl_success or not os.path.exists(temp_file):
                print(f"Download failed for clip {idx}")
                continue
            
            # Process clip (crop to vertical)
            await job_manager.update_job(job_id, {
                "current_stage": f"processing_clip_{idx}",
                "progress": clip_progress + 10
            })
            
            proc_success = await asyncio.to_thread(
                process_clip,
                temp_file,
                cropped_file,
                core_crop_mode
            )
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if not proc_success or not os.path.exists(cropped_file):
                print(f"Processing failed for clip {idx}")
                continue
            
            # Generate subtitle if requested
            subtitle_file = None
            if use_subtitle:
                await job_manager.update_job(job_id, {
                    "current_stage": f"generating_subtitle_{idx}",
                    "progress": clip_progress + 20
                })
                
                try:
                    srt_file = cropped_file.replace(".mp4", ".srt")
                    sub_success = await asyncio.to_thread(
                        generate_subtitle,
                        cropped_file,
                        srt_file,
                        whisper_model,
                        whisper_language
                    )
                    if sub_success:
                        subtitle_file = srt_file
                except Exception as e:
                    print(f"Subtitle failed for clip {idx}: {e}")
            
            # Extract thumbnail
            thumbnail_name = None
            try:
                thumb_file = cropped_file.replace(".mp4", "_thumb.jpg")
                thumb_success = await asyncio.to_thread(
                    extract_thumbnail,
                    cropped_file,
                    thumb_file
                )
                if thumb_success and os.path.exists(thumb_file):
                    thumbnail_name = Path(thumb_file).name
            except Exception as e:
                print(f"Thumbnail failed for clip {idx}: {e}")
            
            # Add clip to job
            clip_info = {
                "filename": Path(cropped_file).name,
                "thumbnail": thumbnail_name,
                "duration": end - start,
                "title": f"Clip {idx} - Viral Moment",
                "description": f"High engagement segment ({segment['score']:.0%})",
                "start_time": segment["start"],
                "end_time": segment["start"] + segment["duration"],
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
