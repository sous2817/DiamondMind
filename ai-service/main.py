import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pose_engine import analyze_video_pose

app = FastAPI(title="DiamondMind AI Service")

# Allow the frontend (or backend) to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open to everyone for now (lock down later)
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a temporary directory for video processing if it doesn't exist
TEMP_DIR = "/tmp/dm_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
def health_check():
    """Simple heartbeat to confirm the service is alive."""
    return {"status": "healthy", "service": "DiamondMind AI"}

@app.post("/analyze/pose")
async def analyze_pose_endpoint(file: UploadFile = File(...)):
    """
    Receives a video file, runs MediaPipe Pose estimation, 
    and returns the skeletal data.
    """
    # 1. Validate File Type
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # 2. Save the Upload to a Temp File
    # We use a UUID to prevent filename collisions (two users uploading 'swing.mp4')
    filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(TEMP_DIR, filename)

    try:
        with open(temp_path, "wb") as buffer:
            # Stream the bytes from the upload to the disk
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Video saved to: {temp_path}")

        # 3. Run the AI Engine (The code you wrote in DM-12!)
        analysis_result = analyze_video_pose(temp_path)

        if "error" in analysis_result:
             raise HTTPException(status_code=500, detail=analysis_result["error"])

        return analysis_result

    except Exception as e:
        print(f"❌ Error processing video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 4. Cleanup (Always run this, even if it crashes)
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"🧹 Cleaned up: {temp_path}")

if __name__ == "__main__":
    import uvicorn
    # Get port from environment (Cloud) or default to 8001 (Local)
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)