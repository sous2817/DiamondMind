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

@app.post("/api/videos/upload")
async def upload_and_analyze(file: UploadFile = File(...), job_id: str = None):
    allowed_extensions = ["mp4", "mov", "avi"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    try:
        files = {"file": (file.filename, file.file, file.content_type)}
        
        async with httpx.AsyncClient(timeout=600.0) as client:
            start_time = time.time()
            logger.info(f"🚀 Sending request to AI Service for Job {job_id}...")
            
            response = await client.post(
                f"{AI_SERVICE_URL}/analyze/pose", 
                files=files,
                params={"job_id": job_id}
            )
            
            duration = time.time() - start_time
            logger.info(f"✅ AI Service responded in {duration:.2f}s with status {response.status_code}")
        
        if response.status_code != 200:
            try:
                ai_data = response.json()
                ai_error = ai_data.get("detail") or ai_data.get("error") or "Unknown AI Error"
            except:
                ai_error = response.text
            raise HTTPException(status_code=response.status_code, detail=f"AI Service: {ai_error}")

        # Append the public download URL to the response
        result = response.json()
        if "video_filename" in result:
             # Construct the Proxy URL for the frontend
             # Note: In production, use your actual domain instead of relying on the request host if behind a proxy
            result["download_url"] = f"/api/videos/download/{result['video_filename']}"

        return result

    except httpx.ReadTimeout:
        logger.error(f"❌ AI Service Timeout after {time.time() - start_time:.2f}s")
        raise HTTPException(status_code=504, detail="AI Processing Timed Out (Limit: 600s)")
    except httpx.ConnectError:
        logger.error("❌ Could not connect to AI Service")
        raise HTTPException(status_code=503, detail="AI Service is currently unreachable.")
    except Exception as e:
        logger.error(f"❌ Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")