"""
YT Heatmap Clipper - Enhanced Version
Extracts viral moments from YouTube videos using heatmap data
"""
import os
import sys
import warnings
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure output encoding
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings("ignore")

# Import core modules
import config
from core import (
    extract_video_id,
    extract_heatmap_data,
    get_video_duration,
    download_video_segment,
    process_clip,
    CropMode,
    generate_subtitle,
    extract_thumbnail,
    detect_facecam_position,
    suggest_crop_mode,
    generate_title,
    generate_description
)
from core.downloader import update_ytdlp
from core.subtitle import check_whisper_installation, install_whisper, get_model_size, is_model_cached


def check_dependencies(install_whisper_pkg: bool = False):
    """
    Ensure required dependencies are available.
    """
    # Update yt-dlp
    print("Checking dependencies...")
    update_ytdlp()
    
    if install_whisper_pkg:
        if not check_whisper_installation():
            print("📦 Installing Faster-Whisper package...")
            if install_whisper():
                print("✅ Faster-Whisper installed successfully.")
            else:
                print("❌ Failed to install Faster-Whisper.")
                return False
        else:
            print("✅ Faster-Whisper package installed.")
        
        # Check model cache
        if is_model_cached(config.WHISPER_MODEL):
            print(f"✅ Model '{config.WHISPER_MODEL}' already cached.\n")
        else:
            print(f"⚠️  Model '{config.WHISPER_MODEL}' not cached.")
            print(f"   📥 Will download ~{get_model_size(config.WHISPER_MODEL)} on first use.\n")
    
    # Check FFmpeg
    import shutil
    if not shutil.which("ffmpeg"):
        print("❌ FFmpeg not found. Please install FFmpeg.")
        return False
    
    return True


def process_single_clip(
    video_id: str,
    segment: Dict,
    index: int,
    total_duration: float,
    crop_mode: CropMode,
    use_subtitle: bool,
    progress_callback: Optional[Callable] = None
) -> bool:
    """
    Process a single clip from start to finish.
    
    Args:
        video_id: YouTube video ID
        segment: Heatmap segment dict
        index: Clip index number
        total_duration: Total video duration
        crop_mode: Crop mode to use
        use_subtitle: Whether to generate subtitle
        progress_callback: Optional progress callback
        
    Returns:
        True if successful, False otherwise
    """
    start_original = segment["start"]
    end_original = segment["start"] + segment["duration"]
    
    # Add padding
    start = max(0, start_original - config.PADDING)
    end = min(end_original + config.PADDING, total_duration)
    
    if end - start < 3:
        return False
    
    # File paths
    temp_file = os.path.join(config.TEMP_DIR, f"temp_{index}.mp4")
    subtitle_file = os.path.join(config.TEMP_DIR, f"temp_{index}.srt") if use_subtitle else None
    output_file = os.path.join(config.OUTPUT_DIR, f"clip_{index}.mp4")
    thumbnail_file = os.path.join(config.OUTPUT_DIR, f"clip_{index}_thumb.jpg")
    
    print(f"\n[Clip {index}] Processing segment ({int(start)}s - {int(end)}s)")
    
    try:
        # Step 1: Download segment
        print("  Downloading segment...")
        if not download_video_segment(video_id, start, end, temp_file, progress_callback):
            return False
        
        # Step 2: Generate subtitle if enabled
        if use_subtitle:
            print("  Generating subtitle...")
            if not generate_subtitle(temp_file, subtitle_file, progress_callback=progress_callback):
                print("  ⚠️  Subtitle generation failed, continuing without subtitle...")
                subtitle_file = None
        
        # Step 3: Process video (crop, subtitle, effects)
        print("  Processing video...")
        if not process_clip(
            temp_file,
            output_file,
            crop_mode,
            subtitle_file,
            progress_callback=progress_callback
        ):
            return False
        
        # Step 4: Extract thumbnail
        if config.THUMBNAIL_ENABLED:
            print("  Extracting thumbnail...")
            extract_thumbnail(output_file, thumbnail_file, progress_callback=progress_callback)
        
        # Cleanup temp files
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if subtitle_file and os.path.exists(subtitle_file):
            os.remove(subtitle_file)
        
        print(f"✅ Clip {index} completed successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to process clip {index}: {str(e)}")
        
        # Cleanup
        for f in [temp_file, subtitle_file]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        
        return False


def process_video(
    url: str,
    crop_mode: CropMode = CropMode.DEFAULT,
    use_subtitle: bool = False,
    max_clips: int = None,
    parallel: bool = False
) -> int:
    """
    Process a YouTube video and generate clips.
    
    Args:
        url: YouTube video URL
        crop_mode: Crop mode to use
        use_subtitle: Whether to generate subtitles
        max_clips: Maximum number of clips (defaults to config.MAX_CLIPS)
        parallel: Whether to process clips in parallel
        
    Returns:
        Number of successfully generated clips
    """
    if max_clips is None:
        max_clips = config.MAX_CLIPS
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        print("❌ Invalid YouTube URL.")
        return 0
    
    print(f"\n📹 Video ID: {video_id}")
    
    # Get heatmap data
    print("📊 Fetching heatmap data...")
    heatmap_segments = extract_heatmap_data(video_id)
    
    if not heatmap_segments:
        print("❌ No high-engagement segments found.")
        return 0
    
    print(f"✅ Found {len(heatmap_segments)} high-engagement segments.")
    
    # Get video duration
    total_duration = get_video_duration(video_id)
    print(f"⏱️  Video duration: {int(total_duration)}s")
    
    # Create output directories
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    
    # Limit to max clips
    segments_to_process = heatmap_segments[:max_clips]
    
    print(f"\n🎬 Processing {len(segments_to_process)} clips...")
    print(f"   Crop mode: {crop_mode.value}")
    print(f"   Subtitle: {'Enabled' if use_subtitle else 'Disabled'}")
    print(f"   Parallel: {'Enabled' if parallel else 'Disabled'}")
    
    success_count = 0
    
    if parallel and config.PARALLEL_WORKERS > 1:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=config.PARALLEL_WORKERS) as executor:
            futures = []
            
            for i, segment in enumerate(segments_to_process, start=1):
                future = executor.submit(
                    process_single_clip,
                    video_id,
                    segment,
                    i,
                    total_duration,
                    crop_mode,
                    use_subtitle
                )
                futures.append(future)
            
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
    else:
        # Sequential processing
        for i, segment in enumerate(segments_to_process, start=1):
            if process_single_clip(
                video_id,
                segment,
                i,
                total_duration,
                crop_mode,
                use_subtitle
            ):
                success_count += 1
    
    return success_count


def batch_process(
    urls: List[str],
    crop_mode: CropMode = CropMode.DEFAULT,
    use_subtitle: bool = False,
    max_clips_per_video: int = None
) -> Dict[str, int]:
    """
    Process multiple YouTube videos.
    
    Args:
        urls: List of YouTube URLs
        crop_mode: Crop mode to use
        use_subtitle: Whether to generate subtitles
        max_clips_per_video: Max clips per video
        
    Returns:
        Dict mapping URL to number of clips generated
    """
    results = {}
    
    print(f"\n📦 Batch processing {len(urls)} videos...")
    
    for i, url in enumerate(urls, start=1):
        print(f"\n{'='*60}")
        print(f"Processing video {i}/{len(urls)}: {url}")
        print('='*60)
        
        count = process_video(url, crop_mode, use_subtitle, max_clips_per_video)
        results[url] = count
    
    return results


def interactive_mode():
    """
    Interactive CLI mode (original behavior).
    """
    print("\n" + "="*60)
    print("YT Heatmap Clipper - Enhanced Version")
    print("="*60)
    
    # Select crop mode
    print("\n=== Crop Mode ===")
    print("1. Default (center crop)")
    print("2. Split 1 (top: center, bottom: bottom-left facecam)")
    print("3. Split 2 (top: center, bottom: bottom-right facecam)")
    
    while True:
        choice = input("\nSelect crop mode (1-3): ").strip()
        if choice == "1":
            crop_mode = CropMode.DEFAULT
            break
        elif choice == "2":
            crop_mode = CropMode.SPLIT_LEFT
            break
        elif choice == "3":
            crop_mode = CropMode.SPLIT_RIGHT
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Ask for subtitle
    print(f"\n=== Auto Subtitle ===")
    print(f"Model: {config.WHISPER_MODEL} (~{get_model_size(config.WHISPER_MODEL)})")
    subtitle_choice = input("Add auto subtitle? (y/n): ").strip().lower()
    use_subtitle = subtitle_choice in ["y", "yes"]
    
    # Check dependencies
    if not check_dependencies(install_whisper_pkg=use_subtitle):
        return
    
    # Get video URL
    url = input("\nYouTube URL: ").strip()
    
    # Process video
    success_count = process_video(url, crop_mode, use_subtitle)
    
    print(f"\n{'='*60}")
    print(f"✅ Finished! {success_count} clips saved to '{config.OUTPUT_DIR}'")
    print('='*60)


def main():
    """
    Main entry point.
    """
    # Check if running in CLI mode with arguments
    if len(sys.argv) > 1:
        # TODO: Add argparse for CLI arguments
        # For now, just run interactive mode
        pass
    
    # Run interactive mode
    interactive_mode()


if __name__ == "__main__":
    main()
