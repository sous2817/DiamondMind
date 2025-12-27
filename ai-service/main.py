import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pose_engine import PoseAnalyzer
import os

app = FastAPI()
pose_analyzer = PoseAnalyzer()

class VideoAnalysisRequest(BaseModel):
    video_path: str

@app.get("/")
def health_check():
    return {"status": "active", "service": "diamond-mind-ai-v1"}

@app.post("/analyze/pose")
def analyze_pose(request: VideoAnalysisRequest):
    """
    DM-12: Takes a local video path, returns 33-point skeletal JSON.
    """
    video_path = request.video_path
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail=f"Video not found at path: {video_path}")

    try:
        # Run the analysis
        result = pose_analyzer.process_video(video_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)