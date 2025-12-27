import cv2
import mediapipe as mp
import numpy as np

def analyze_video_pose(video_path: str):
    """
    Reads a video file, runs MediaPipe Pose 'Heavy', 
    and returns a list of landmarks for every frame.
    """
    
    # Initialize MediaPipe Pose
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Define the model path
    model_path = 'pose_landmarker_heavy.task'

    # Create the landmarker instance
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO
    )

    try:
        landmarker = PoseLandmarker.create_from_options(options)
    except Exception as e:
        return {"error": f"Failed to load MediaPipe model: {e}"}

    # Open the video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": f"Could not open video file: {video_path}"}

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    results = []

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

        # Extract data if found
        frame_data = {
            "frame": frame_count,
            "timestamp": timestamp_ms,
            "landmarks": []
        }

        if detection_result.pose_landmarks:
            # We only care about the first person detected [0]
            for i, landmark in enumerate(detection_result.pose_landmarks[0]):
                frame_data["landmarks"].append({
                    "id": i,
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                })
        
        results.append(frame_data)
        frame_count += 1

    cap.release()
    landmarker.close()

    return {
        "metadata": {
            "total_frames": frame_count,
            "fps": fps
        },
        "frames": results
    }