"""
FastAPI main application
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from api.routes import router
from api.websocket import websocket_endpoint
from api.job_manager import job_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting YT Heatmap Clipper API...")
    
    # Ensure directories exist
    os.makedirs("jobs", exist_ok=True)
    os.makedirs("clips", exist_ok=True)
    
    # Load existing jobs
    await job_manager.load_jobs()
    
    # Start cleanup task
    job_manager.start_cleanup_task()
    
    yield
    
    # Shutdown
    print("🛑 Shutting down YT Heatmap Clipper API...")
    job_manager.stop_cleanup_task()


app = FastAPI(
    title="YT Heatmap Clipper API",
    description="API for processing YouTube videos into viral clips using heatmap data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for clips
if os.path.exists("clips"):
    app.mount("/clips", StaticFiles(directory="clips"), name="clips")

# Include routes
app.include_router(router, prefix="/api")

# WebSocket endpoint
app.add_api_websocket_route("/ws/progress/{job_id}", websocket_endpoint)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "YT Heatmap Clipper API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "api": "/api",
            "websocket": "/ws/progress/{job_id}"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "jobs": {
            "active": len([j for j in job_manager.jobs.values() if j["status"] in ["queued", "processing"]]),
            "total": len(job_manager.jobs)
        }
    }
