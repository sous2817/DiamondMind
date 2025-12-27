import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import os
import numpy as np

class PoseAnalyzer:
    def __init__(self, model_path="pose_landmarker.task"):
        """
        Initializes the MediaPipe Pose Landmarker using the new 'Tasks' API.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}. Please download it!")

        # Create the BaseOptions (loads the model file)
        base_options = python.BaseOptions(model_asset_path=model_path)

        # Set running mode to VIDEO (optimized for time-series tracking)
        # Note: We use VIDEO mode because we are processing frames sequentially.
        VisionRunningMode = vision.RunningMode
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=VisionRunningMode.VIDEO,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_segmentation_masks=False
        )

        # Create the Landmarker
        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def process_video(self, video_path: str):
        if not os.path.exists(video_path):
            return {"error": "Video file not found"}

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        output_data = {
            "metadata": {
                "video_file": os.path.basename(video_path),
                "fps": fps,
                "total_frames": frame_count
            },
            "frames": []
        }

        print(f"🎬 Processing {frame_count} frames with MediaPipe Tasks...")
        start_time = time.time()

        frame_idx = 0
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Convert OpenCV (BGR) image to MediaPipe Image (RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            
            # Timestamp is REQUIRED for VIDEO mode (in milliseconds)
            timestamp_ms = int((frame_idx / fps) * 1000)

            # --- DETECT ---
            detection_result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
            
            frame_data = {
                "frame_index": frame_idx,
                "timestamp_ms": timestamp_ms,
                "landmarks": []
            }

            # Extract landmarks (if any)
            if detection_result.pose_landmarks:
                # We usually care about the first person detected [0]
                landmarks = detection_result.pose_landmarks[0]
                
                for i, landmark in enumerate(landmarks):
                    frame_data["landmarks"].append({
                        "id": i,
                        # The new API doesn't give names (like "NOSE") directly in the loop,
                        # but the index 0-32 matches the old standard.
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility,
                        "presence": landmark.presence 
                    })
            else:
                frame_data["error"] = "No body detected"

            output_data["frames"].append(frame_data)
            frame_idx += 1

        cap.release()
        
        duration = time.time() - start_time
        print(f"✅ Processing complete in {duration:.2f} seconds.")
        
        return output_data

if __name__ == "__main__":
    analyzer = PoseAnalyzer()
    print("Pose Engine (Tasks API) initialized successfully.")