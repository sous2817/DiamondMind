import cv2
import mediapipe as mp
import numpy as np
import requests

def analyze_video_pose(video_path: str, job_id: str = None):
    """
    Reads a video file, runs MediaPipe Pose 'Heavy', 
    and returns a list of landmarks for every frame.
    """
    
    # 1. Setup MediaPipe
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    model_path = 'pose_landmarker_heavy.task'
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO
    )

    try:
        landmarker = PoseLandmarker.create_from_options(options)
    except Exception as e:
        return {"error": f"Failed to load MediaPipe model: {e}"}

    # 2. Open the video inside the function
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": f"Could not open video file: {video_path}"}

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    results = []

    # 3. Processing Loop
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Calculate timestamp in milliseconds
        timestamp_ms = int((frame_count / fps) * 1000)

        # Detect landmarks
        detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

        # Extract data
        frame_data = {
            "frame": frame_count,
            "timestamp": timestamp_ms,
            "landmarks": []
        }

        if detection_result.pose_landmarks:
            # Get landmarks for the first detected person
            for i, landmark in enumerate(detection_result.pose_landmarks[0]):
                frame_data["landmarks"].append({
                    "id": i,
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                })
        
        results.append(frame_data)

        # PROGRESS PULSE: Every 10 frames, notify the backend
        if job_id and frame_count % 10 == 0:
            progress = int((frame_count / total_frames) * 100)
            try:
                # We use a timeout so the AI isn't held up by a slow pulse
                requests.post(
                    f"https://diamondmind-vg35.onrender.com/api/jobs/{job_id}/progress",
                    json={"progress": progress},
                    timeout=0.5 
                )
            except Exception as e:
                print(f"Pulse failed: {e}")

        frame_count += 1

    # 4. Cleanup
    cap.release()
    landmarker.close()

    return {
        "metadata": {
            "total_frames": frame_count,
            "fps": fps
        },
        "frames": results
    }