import os
import shutil
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pose_engine import PoseExtractor
import traceback

app = FastAPI(title="DiamondMind AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = tempfile.gettempdir()
print(f"📂 AI Service using temp dir: {TEMP_DIR}")

print("🧠 Initializing AI Model...")
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

    filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(TEMP_DIR, filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"▶️ Starting Analysis for Job: {job_id}")

        # Pass TEMP_DIR so the engine knows where to save the output video
        pose_data = ai_engine.process_video(temp_path, job_id=job_id, output_dir=TEMP_DIR)
        
        print(f"🏁 Analysis Complete. Video ready: {pose_data.get('video_filename')}")
        return pose_data

    except Exception as e:
        print("❌ CRITICAL ERROR IN ANALYZE ENDPOINT:")
        traceback.print_exc()  # This prints the red error text to the console
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup input file only
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"🧹 Cleaned up input: {temp_path}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)