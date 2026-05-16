# utils/progress_handler.py
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
import json

class ProgressHandler:
    """Handles progress updates for video generation"""
    
    def __init__(self, send_callback):
        """
        Args:
            send_callback: Async function to send progress updates
        """
        self.send = send_callback
    
    async def step_start(self, step: str, message: str = ""):
        """Send step start progress"""
        await self.send({
            "type": "step_start",
            "step": step,
            "message": message or f"Starting {step}...",
            "timestamp": datetime.now().isoformat()
        })
    
    async def step_complete(self, step: str, message: str = "", data: Optional[Dict] = None):
        """Send step complete progress"""
        update = {
            "type": "step_complete",
            "step": step,
            "message": message or f"{step.upper()} completed",
            "timestamp": datetime.now().isoformat()
        }
        if data:
            update["data"] = data
        await self.send(update)
    
    async def step_error(self, step: str, error: str):
        """Send step error progress"""
        await self.send({
            "type": "step_error",
            "step": step,
            "message": error,
            "timestamp": datetime.now().isoformat()
        })
    
    async def progress_update(self, step: str, progress: int, message: str = ""):
        """Send progress update (0-100)"""
        await self.send({
            "type": "progress",
            "step": step,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })