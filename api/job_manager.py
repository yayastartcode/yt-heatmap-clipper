"""
Job queue and state management
"""
import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta

from api.models import JobStatus


class JobManager:
    """Manages job queue and state"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.jobs_dir = Path("jobs")
        self.jobs_dir.mkdir(exist_ok=True)
        self.cleanup_task: Optional[asyncio.Task] = None
        self.progress_callbacks: Dict[str, list] = {}
        
    async def create_job(self, job_data: Dict[str, Any]) -> str:
        """Create a new job"""
        job_id = str(uuid.uuid4())
        
        job = {
            "job_id": job_id,
            "status": JobStatus.QUEUED,
            "progress": 0.0,
            "clips_done": 0,
            "total_clips": 0,
            "current_stage": None,
            "error": None,
            "created_at": time.time(),
            "updated_at": time.time(),
            "data": job_data,
            "clips": []
        }
        
        self.jobs[job_id] = job
        await self._save_job(job_id)
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    async def update_job(self, job_id: str, updates: Dict[str, Any]):
        """Update job state"""
        if job_id not in self.jobs:
            return
        
        self.jobs[job_id].update(updates)
        self.jobs[job_id]["updated_at"] = time.time()
        
        await self._save_job(job_id)
        
        # Notify WebSocket listeners
        await self._notify_progress(job_id)
    
    async def add_clip(self, job_id: str, clip_info: Dict[str, Any]):
        """Add a completed clip to job"""
        if job_id not in self.jobs:
            return
        
        self.jobs[job_id]["clips"].append(clip_info)
        self.jobs[job_id]["clips_done"] = len(self.jobs[job_id]["clips"])
        self.jobs[job_id]["updated_at"] = time.time()
        
        await self._save_job(job_id)
        await self._notify_progress(job_id)
    
    def register_progress_callback(self, job_id: str, callback: Callable):
        """Register a callback for progress updates"""
        if job_id not in self.progress_callbacks:
            self.progress_callbacks[job_id] = []
        self.progress_callbacks[job_id].append(callback)
    
    def unregister_progress_callback(self, job_id: str, callback: Callable):
        """Unregister a progress callback"""
        if job_id in self.progress_callbacks:
            self.progress_callbacks[job_id].remove(callback)
            if not self.progress_callbacks[job_id]:
                del self.progress_callbacks[job_id]
    
    async def _notify_progress(self, job_id: str):
        """Notify all registered callbacks about progress"""
        if job_id not in self.progress_callbacks:
            return
        
        job = self.jobs.get(job_id)
        if not job:
            return
        
        for callback in self.progress_callbacks[job_id]:
            try:
                await callback(job)
            except Exception as e:
                print(f"Error in progress callback: {e}")
    
    async def _save_job(self, job_id: str):
        """Save job state to disk"""
        job = self.jobs.get(job_id)
        if not job:
            return
        
        job_file = self.jobs_dir / f"{job_id}.json"
        
        # Convert to JSON-serializable format
        job_data = {
            **job,
            "status": job["status"].value if isinstance(job["status"], JobStatus) else job["status"]
        }
        
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=2)
    
    async def load_jobs(self):
        """Load existing jobs from disk"""
        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with open(job_file) as f:
                    job = json.load(f)
                    job_id = job["job_id"]
                    
                    # Convert status string back to enum
                    job["status"] = JobStatus(job["status"])
                    
                    self.jobs[job_id] = job
                    print(f"Loaded job: {job_id}")
            except Exception as e:
                print(f"Error loading job {job_file}: {e}")
    
    def start_cleanup_task(self):
        """Start background cleanup task"""
        self.cleanup_task = asyncio.create_task(self._cleanup_old_jobs())
    
    def stop_cleanup_task(self):
        """Stop background cleanup task"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
    
    async def _cleanup_old_jobs(self):
        """Clean up jobs older than 24 hours"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff_time = time.time() - (24 * 3600)  # 24 hours ago
                
                jobs_to_remove = []
                for job_id, job in self.jobs.items():
                    if job["created_at"] < cutoff_time:
                        jobs_to_remove.append(job_id)
                
                for job_id in jobs_to_remove:
                    # Remove job file
                    job_file = self.jobs_dir / f"{job_id}.json"
                    if job_file.exists():
                        job_file.unlink()
                    
                    # Remove from memory
                    del self.jobs[job_id]
                    print(f"Cleaned up old job: {job_id}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in cleanup task: {e}")


# Global job manager instance
job_manager = JobManager()
