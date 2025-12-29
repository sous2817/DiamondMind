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

@app.post("/api/videos/upload")
async def upload_and_analyze(file: UploadFile = File(...), job_id: str = None):
    """
    Gateway endpoint: Receives video, forwards to AI Service, returns JSON.
    Includes job_id for real-time progress tracking via WebSockets.
    """
    # 1. Validate file extension
    allowed_extensions = ["mp4", "mov", "avi"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    try:
        # 2. Read the file into memory
        file_content = await file.read()
        
        # 3. Prepare payload for AI Service
        files = {"file": (file.filename, file_content, file.content_type)}
        
        # 4. Forward to AI Service with job_id as a query parameter
        # Note: Added params={"job_id": job_id} to the post call
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/analyze/pose", 
                files=files,
                params={"job_id": job_id}
            )
        
        if response.status_code != 200:
            # Handle the specific 'cap' error or others from AI Service
            ai_data = response.json()
            ai_error = ai_data.get("detail") or ai_data.get("error") or "Unknown AI Error"
            raise HTTPException(status_code=response.status_code, detail=f"AI Service: {ai_error}")

        return response.json()

    except httpx.ConnectError as e:
        # PRINT THIS
        print(f"❌ CONNECTION ERROR to AI Service: {e}")
        raise HTTPException(status_code=503, detail="AI Service is unreachable.")
        
    except Exception as e:
        # PRINT THIS
        import traceback
        traceback.print_exc() # <--- This will print the full stack trace to Render logs
        print(f"❌ GENERIC ERROR: {e}") 
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
        