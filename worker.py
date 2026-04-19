"""
Main worker entry point for YT Heatmap Clipper

This script starts:
1. FastAPI backend server
2. Telegram bot (optional, if TELEGRAM_BOT_TOKEN is set)

Usage:
    python worker.py                    # Start API only
    python worker.py --with-bot         # Start API + Telegram bot
    python worker.py --bot-only         # Start Telegram bot only
"""
import os
import sys
import asyncio
import argparse
import uvicorn
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config


async def run_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Run FastAPI server"""
    config = uvicorn.Config(
        "api.main:app",
        host=host,
        port=port,
        log_level="info",
        reload=False
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_telegram_bot():
    """Run Telegram bot"""
    from bot.telegram_bot import run_bot
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set in environment")
        return
    
    await run_bot(token)


async def run_both(host: str = "0.0.0.0", port: int = 8000):
    """Run both API server and Telegram bot"""
    # Run both concurrently
    await asyncio.gather(
        run_api_server(host, port),
        run_telegram_bot()
    )


def cleanup_old_jobs():
    """Clean up old jobs and clips"""
    import json
    import time
    from datetime import datetime, timedelta
    
    jobs_dir = Path("jobs")
    clips_dir = Path("clips")
    
    if not jobs_dir.exists():
        print("No jobs directory found")
        return
    
    # Calculate cutoff time
    cutoff_time = time.time() - (config.MAX_JOB_AGE_HOURS * 3600)
    
    deleted_jobs = 0
    deleted_clips = 0
    
    # Clean up old jobs
    for job_file in jobs_dir.glob("*.json"):
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            created_at = job_data.get("created_at", 0)
            
            if created_at < cutoff_time:
                # Delete associated clips
                for clip in job_data.get("clips", []):
                    clip_path = clips_dir / clip["filename"]
                    if clip_path.exists():
                        clip_path.unlink()
                        deleted_clips += 1
                    
                    if clip.get("thumbnail"):
                        thumb_path = clips_dir / clip["thumbnail"]
                        if thumb_path.exists():
                            thumb_path.unlink()
                            deleted_clips += 1
                
                # Delete job file
                job_file.unlink()
                deleted_jobs += 1
                
                print(f"Deleted old job: {job_file.stem}")
        
        except Exception as e:
            print(f"Error processing {job_file}: {e}")
    
    print(f"\nDeleted {deleted_jobs} jobs and {deleted_clips} files")
    
    # Check disk usage
    if clips_dir.exists():
        import shutil
        total, used, free = shutil.disk_usage(clips_dir)
        used_gb = used / (1024**3)
        print(f"Disk usage: {used_gb:.2f} GB")
        
        if used_gb > config.MAX_DISK_USAGE_GB:
            print(f"⚠️  Warning: Disk usage exceeds {config.MAX_DISK_USAGE_GB} GB")


def test_youtube_connectivity():
    """Test YouTube connectivity with all strategies"""
    from core.downloader import test_youtube_connectivity as test_yt
    
    print("\nTesting YouTube download strategies...\n")
    
    results = test_yt()
    
    print(f"OAuth tokens available: {'✅' if results['oauth_available'] else '❌'}")
    print(f"Cookies file available: {'✅' if results['cookies_available'] else '❌'}")
    print(f"Deno available: {'✅' if results['deno_available'] else '❌'}")
    print("\nStrategy test results:")
    
    for strategy, result in results['strategies'].items():
        status = "✅ Success" if result['success'] else f"❌ Failed: {result['error']}"
        print(f"  {strategy}: {status}")
    
    # Test LLM connectivity
    print("\n\nTesting LLM connectivity...")
    if config.LLM_API_URL and config.LLM_API_KEY:
        try:
            import requests
            response = requests.get(
                config.LLM_API_URL.replace("/v1/chat/completions", "/health"),
                timeout=5
            )
            if response.status_code == 200:
                print(f"✅ LLM API accessible at {config.LLM_API_URL}")
            else:
                print(f"⚠️  LLM API returned status {response.status_code}")
        except Exception as e:
            print(f"❌ LLM API error: {e}")
    else:
        print("❌ LLM API not configured")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="YT Heatmap Clipper Worker")
    parser.add_argument("--host", default="0.0.0.0", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    parser.add_argument("--with-bot", action="store_true", help="Start with Telegram bot")
    parser.add_argument("--bot-only", action="store_true", help="Start Telegram bot only")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old jobs and exit")
    parser.add_argument("--test", action="store_true", help="Test YouTube connectivity and exit")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎬 YT Heatmap Clipper Worker")
    print("=" * 60)
    
    # Handle cleanup mode
    if args.cleanup:
        print("\n🧹 Running cleanup...")
        cleanup_old_jobs()
        print("✅ Cleanup complete")
        return
    
    # Handle test mode
    if args.test:
        print("\n🔍 Testing YouTube connectivity...")
        test_youtube_connectivity()
        return
    
    if args.bot_only:
        print("Starting Telegram bot only...")
        asyncio.run(run_telegram_bot())
    
    elif args.with_bot:
        print(f"Starting API server on {args.host}:{args.port} + Telegram bot...")
        asyncio.run(run_both(args.host, args.port))
    
    else:
        print(f"Starting API server on {args.host}:{args.port}...")
        asyncio.run(run_api_server(args.host, args.port))


if __name__ == "__main__":
    main()
