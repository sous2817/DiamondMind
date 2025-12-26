# C:\dm\ai-service\main.py
import sys
import uvicorn
from fastapi import FastAPI

app = FastAPI()

# --- SMOKE TEST: Try to import heavy libraries ---
try:
    import cv2
    import mediapipe as mp
    import numpy as np
    print(f"SUCCESS: OpenCV version {cv2.__version__}")
    print(f"SUCCESS: MediaPipe version {mp.__version__}")
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import AI libraries: {e}")
    sys.exit(1)

@app.get("/")
def health_check():
    return {
        "status": "active",
        "service": "diamond-mind-ai",
        "opencv": cv2.__version__,
        "mediapipe": mp.__version__
    }

if __name__ == "__main__":
    # Run on port 8001 to avoid conflict with Backend (8000)
    uvicorn.run(app, host="127.0.0.1", port=8001)