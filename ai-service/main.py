import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# UPDATED IMPORT: We import the class, not the old function
from pose_engine import PoseExtractor

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

# --- CRITICAL OPTIMIZATION ---
# Initialize the AI Engine ONCE when the server starts.
# This prevents reloading the heavy ML model for every single request.
# We use model_complexity=0 (Lite) for maximum speed.
print("🧠 Initializing AI Model...")
ai_engine = PoseExtractor(model_complexity=0)
print("✅ AI Model Ready.")

@app.get("/")
def health_check():
    """Simple heartbeat to confirm the service is alive."""
    return {"status": "healthy", "service": "DiamondMind AI"}

@app.post("/analyze/pose")
async def analyze(file: UploadFile = File(...), job_id: str = None):
    """
    Receives a video file, runs MediaPipe Pose estimation, 
    and returns the skeletal data.
    """
    # 1. Validate File Type
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # 2. Save the Upload to a Temp File
    filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(TEMP_DIR, filename)

    try:
        with open(temp_path, "wb") as buffer:
            # Stream the bytes from the upload to the disk
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Video saved to: {temp_path}")

        # 3. Run the AI Engine (Using the Class Instance)
        print(f"▶️ Starting Analysis for Job: {job_id}")
        pose_data = ai_engine.process_video(temp_path)
        print(f"🏁 Analysis Complete. Extracted {len(pose_data)} frames.")

        # 4. Return Structured Data
        return {
            "job_id": job_id,
            "status": "success",
            "data": pose_data  # The list of frames
        }

    except Exception as e:
        print(f"❌ Error processing video: {e}")
        # Return 500 so the Backend knows to retry or fail
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 5. Cleanup (Always run this, even if it crashes)
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"🧹 Cleaned up: {temp_path}")

if __name__ == "__main__":
    import uvicorn
    # Get port from environment (Cloud) or default to 8001 (Local)
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)