"""
WebSocket handler for real-time progress updates
"""
import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

from api.job_manager import job_manager
from api.models import ProgressMessage


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, job_id: str, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        
        self.active_connections[job_id].add(websocket)
        
        # Register progress callback
        callback = self._create_callback(websocket)
        job_manager.register_progress_callback(job_id, callback)
        
        # Send initial job state
        job = job_manager.get_job(job_id)
        if job:
            await self._send_job_update(websocket, job)
    
    def disconnect(self, job_id: str, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    def _create_callback(self, websocket: WebSocket):
        """Create a progress callback for a WebSocket"""
        async def callback(job: dict):
            await self._send_job_update(websocket, job)
        return callback
    
    async def _send_job_update(self, websocket: WebSocket, job: dict):
        """Send job update to WebSocket"""
        try:
            message = ProgressMessage(
                type="progress",
                job_id=job["job_id"],
                clip=job["clips_done"],
                total=job["total_clips"],
                stage=job.get("current_stage", ""),
                percent=job["progress"],
                message=job.get("error")
            )
            
            await websocket.send_json(message.model_dump())
        
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")
    
    async def broadcast(self, job_id: str, message: dict):
        """Broadcast message to all connections for a job"""
        if job_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(job_id, connection)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates
    
    Usage:
        ws://localhost:8000/ws/progress/{job_id}
    
    Messages:
        {
            "type": "progress",
            "job_id": "...",
            "clip": 1,
            "total": 5,
            "stage": "downloading|cropping|subtitle",
            "percent": 75.0,
            "message": "Optional status message"
        }
    """
    await manager.connect(job_id, websocket)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        manager.disconnect(job_id, websocket)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(job_id, websocket)
