import httpx
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

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

# Endpoint for the AI Service to report progress
@app.post("/api/jobs/{job_id}/progress")
async def receive_progress(job_id: str, data: dict):
    await manager.send_progress(job_id, data["progress"])
    return {"status": "ok"}

# WebSocket for the Mobile Phone to listen
@app.websocket("/ws/progress/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(job_id, websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(job_id)

# 1. Update CORS to allow your Vercel Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your Vercel URL later for security
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Get the AI Service URL from Environment Variables
AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8001")

# --- HELPER: STREAMING GENERATOR ---
async def stream_file(file: UploadFile):
    """Yields file chunks to prevent loading entire video into memory."""
    while chunk := await file.read(1024 * 1024):  # Read 1MB chunks
        yield chunk

@app.post("/api/videos/upload")
async def upload_and_analyze(file: UploadFile = File(...), job_id: str = None):
    """
    Gateway endpoint: Streams video directly to AI Service.
    Uses generator to avoid RAM spikes on Render Free Tier.
    """
    # 1. Validate file extension
    allowed_extensions = ["mp4", "mov", "avi"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    try:
        # 2. Prepare the streaming upload (NO reading into variable!)
        # We manually construct the multipart stream
        files = {"file": (file.filename, stream_file(file), file.content_type)}
        
        # 3. Forward to AI Service with extended timeout
        async with httpx.AsyncClient(timeout=300.0) as client: # Increased to 300s
            response = await client.post(
                f"{AI_SERVICE_URL}/analyze/pose", 
                files=files,
                params={"job_id": job_id}
            )
        
        if response.status_code != 200:
            # Handle the specific 'cap' error or others from AI Service
            try:
                ai_data = response.json()
                ai_error = ai_data.get("detail") or ai_data.get("error") or "Unknown AI Error"
            except:
                ai_error = response.text
            raise HTTPException(status_code=response.status_code, detail=f"AI Service: {ai_error}")

        return response.json()

    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="AI Processing Timed Out (Limit: 300s)")

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="AI Service is currently unreachable.")
        
    except Exception as e:
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")