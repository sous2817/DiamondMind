import os
import shutil
import uuid
import tempfile  # 👈 Added
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pose_engine import PoseExtractor

app = FastAPI(title="DiamondMind AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ FIX: Use the system's correct temp directory (works on Windows & Linux)
TEMP_DIR = tempfile.gettempdir()
print(f"📂 Using temporary directory: {TEMP_DIR}")

print("🧠 Initializing AI Model...")
# Ensure model_complexity matches what your machine can handle (0=Lite, 1=Full)
ai_engine = PoseExtractor(model_complexity=0)
print("✅ AI Model Ready.")

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "DiamondMind AI"}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)

@app.post("/analyze/pose")
async def analyze(file: UploadFile = File(...), job_id: str = None):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Use unique name for input
    filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(TEMP_DIR, filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"▶️ Starting Analysis for Job: {job_id}")
        
        # ⚠️ CRITICAL: Ensure pose_engine.py is also using tempfile.gettempdir()
        # or passing the output path explicitly. Ideally, we pass the directory:
        pose_data = ai_engine.process_video(temp_path, job_id=job_id, output_dir=TEMP_DIR)
        
        print(f"🏁 Analysis Complete. Output: {pose_data.get('video_filename')}")

        return pose_data

    except Exception as e:
        print(f"❌ Error processing video: {e}")
        # Print the full traceback to the console so we can see the line number
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"🧹 Cleaned up input: {temp_path}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)