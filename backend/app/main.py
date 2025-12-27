import httpx
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DiamondMind Main Backend")

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
async def upload_and_analyze(file: UploadFile = File(...)):
    """
    Gateway endpoint: Receives video, forwards to AI Service, returns JSON.
    """
    # Validate file extension
    allowed_extensions = ["mp4", "mov", "avi"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    try:
        # Read the file into memory (limited to 50MB by our constraint)
        file_content = await file.read()
        
        # Prepare the 'multipart/form-data' payload for the AI Service
        files = {"file": (file.filename, file_content, file.content_type)}

        # Forward the request to the AI Service with a generous timeout
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{AI_SERVICE_URL}/analyze/pose", files=files)
        
        if response.status_code != 200:
            ai_error = response.json().get("detail", "Unknown AI Error")
            raise HTTPException(status_code=response.status_code, detail=f"AI Service: {ai_error}")

        return response.json()

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="AI Service is currently unreachable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))