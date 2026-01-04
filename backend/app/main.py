import httpx
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(title="DiamondMind Main Backend")

import shutil
from fastapi import BackgroundTasks

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_progress(self, job_id: str, progress: int):
        if job_id in self.active_connections:
            await self.active_connections[job_id].send_json({"progress": progress})

    async def send_result(self, job_id: str, result: dict):
        if job_id in self.active_connections:
            await self.active_connections[job_id].send_json({"result": result})

    async def send_error(self, job_id: str, message: str):
        if job_id in self.active_connections:
            # Strip HTML error pages and replace with friendly messages
            if message.strip().startswith("<!DOCTYPE") or message.strip().startswith("<html"):
                # Extract status code if present
                if "504" in message:
                    clean_msg = "AI service timeout - please try again"
                elif "503" in message:
                    clean_msg = "AI service unavailable - service may be starting up"
                elif "502" in message:
                    clean_msg = "AI service connection error"
                else:
                    clean_msg = "AI service error - please retry"
            else:
                # For non-HTML errors, keep first 150 chars
                clean_msg = message[:150] if len(message) > 150 else message
            
            await self.active_connections[job_id].send_json({"error": clean_msg})

manager = ConnectionManager()

@app.post("/api/jobs/{job_id}/progress")
async def receive_progress(job_id: str, data: dict):
    await manager.send_progress(job_id, data["progress"])
    return {"status": "ok"}

@app.websocket("/ws/progress/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(job_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(job_id)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8001")

# ✅ NEW: Proxy Endpoint for Downloads
@app.get("/api/videos/download/{filename}")
async def download_video(filename: str):
    """Proxies the file download from AI Service to the Client."""
    async def iterfile():
        async with httpx.AsyncClient(timeout=600.0) as client:
            async with client.stream("GET", f"{AI_SERVICE_URL}/download/{filename}") as r:
                if r.status_code != 200:
                    raise HTTPException(status_code=r.status_code, detail="Could not retrieve video")
                async for chunk in r.aiter_bytes():
                    yield chunk

    return StreamingResponse(iterfile(), media_type="video/mp4")

async def process_video_background(file_data: bytes, filename: str, content_type: str, job_id: str):
    """Refactored async processor - saves file in background"""
    print(f"Background: 🎬 Starting processing for Job {job_id}")
    temp_path = None
    try:
        # Save file to temp in background
        temp_dir = "/tmp" if os.path.exists("/tmp") else "."
        ext = filename.split(".")[-1].lower()
        temp_path = os.path.join(temp_dir, f"upload_{job_id}.{ext}")
        
        print(f"Background: 💾 Saving file to {temp_path}...")
        with open(temp_path, "wb") as f:
            f.write(file_data)
        print(f"Background: ✅ File saved ({len(file_data)} bytes)")
        
        # Stream to AI Service
        with open(temp_path, "rb") as f:
            files = {"file": (filename, f, content_type)}
            
            # Explicit Timeout - 15 minutes to handle cold starts
            timeout_config = httpx.Timeout(900.0, connect=60.0)

            async with httpx.AsyncClient(timeout=timeout_config) as client:
                start_time = time.time()
                print(f"Background: 📤 Sending to AI Service for Job {job_id}...")
                response = await client.post(
                    f"{AI_SERVICE_URL}/analyze/pose", 
                    files=files,
                    params={"job_id": job_id}
                )
                duration = time.time() - start_time
                print(f"Background: ✅ AI Service responded in {duration:.2f}s")

        if response.status_code == 200:
             result = response.json()
             if "video_filename" in result:
                result["download_url"] = f"/api/videos/download/{result['video_filename']}"
             await manager.send_result(job_id, result)
        else:
            # Truncate long error responses (e.g., HTML error pages)
            error_text = response.text[:200] if len(response.text) > 200 else response.text
            error_msg = f"AI Error {response.status_code}: {error_text}"
            print(f"Background Error: {error_msg}")
            await manager.send_error(job_id, error_msg)

    except Exception as e:
        error_str = str(e)[:200] if len(str(e)) > 200 else str(e)
        print(f"Background Exception: {error_str}")
        await manager.send_error(job_id, str(e))
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Background: 🧹 Cleaned up {temp_path}")

@app.post("/api/videos/upload")
async def upload_and_analyze(file: UploadFile = File(...), job_id: str = None):
    """
    ⚡️ ASYNC UPLOAD PATTERN:
    1. Read file into memory immediately (non-blocking)
    2. Return 202 Accepted ASAP (prevents load balancer timeout)
    3. Save & Process file in background task
    4. Push results via WebSocket
    """
    allowed_extensions = ["mp4", "mov", "avi"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    try:
        print(f"Backend: 📥 Received upload request for Job {job_id}")
        
        # ⚡️ KEY FIX: Read file into memory WITHOUT blocking the response
        # This is fast enough (<5s) to avoid timeout, then we return immediately
        file_data = await file.read()
        file_size_mb = len(file_data) / (1024 * 1024)
        print(f"Backend: 📦 File read into memory ({file_size_mb:.2f} MB)")
        
        # ⚡️ IMMEDIATE RESPONSE: Return 202 before any processing
        # This closes the HTTP connection in <5 seconds, avoiding the 60s timeout
        import asyncio
        asyncio.create_task(
            process_video_background(file_data, file.filename, file.content_type, job_id)
        )
        
        print(f"Backend: ✅ Returning 202 Accepted (Job {job_id} queued)")
        return {"status": "processing", "message": "Video accepted for background processing", "job_id": job_id}

    except Exception as e:
        logger.error(f"❌ Upload Handling Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))