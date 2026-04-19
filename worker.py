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


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="YT Heatmap Clipper Worker")
    parser.add_argument("--host", default="0.0.0.0", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    parser.add_argument("--with-bot", action="store_true", help="Start with Telegram bot")
    parser.add_argument("--bot-only", action="store_true", help="Start Telegram bot only")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎬 YT Heatmap Clipper Worker")
    print("=" * 60)
    
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
