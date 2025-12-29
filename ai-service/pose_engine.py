import mediapipe
print(f"Loading MediaPipe from: {mediapipe.__file__}")
import cv2
import mediapipe as mp
import numpy as np
import json
import os

class PoseExtractor:
    # OPTIMIZATION: Default model_complexity set to 0 (Lite) for speed on Render Free Tier
    def __init__(self, static_image_mode=False, model_complexity=0, min_detection_confidence=0.5):
        """
        Initialize the MediaPipe Pose model.
        params:
            static_image_mode: False for video (uses tracking to be faster/smoother)
            model_complexity: 0 (Lite), 1 (Full), or 2 (Heavy). 
                              0 is fastest and prevents timeouts on mobile clients.
            min_detection_confidence: Threshold to consider a person detected
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )

    def process_video(self, video_path):
        """
        Reads a video file and extracts skeletal landmarks for every frame.
        Returns a list of dictionaries (one per frame).
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        output_data = []

        print(f"🎬 Starting processing for: {video_path}...")

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # MediaPipe requires RGB input (OpenCV loads as BGR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # --- THE AI MAGIC ---
            # Process the image to detect pose
            results = self.pose.process(frame_rgb)

            # Structure the data for this frame
            frame_data = {
                "frame_index": frame_count,
                "timestamp_ms": cap.get(cv2.CAP_PROP_POS_MSEC),
                "landmarks": {}
            }

            if results.pose_landmarks:
                # Extract the 33 landmarks
                # We normalize them to the list of named landmarks in MediaPipe
                for idx, landmark in enumerate(results.pose_landmarks.landmark):
                    landmark_name = self.mp_pose.PoseLandmark(idx).name
                    frame_data["landmarks"][landmark_name] = {
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    }
            else:
                # Handle occlusion/missing data (as per ticket edge case)
                frame_data["landmarks"] = None 

            output_data.append(frame_data)
            frame_count += 1

        cap.release()
        print(f"✅ Processing complete. Extracted {len(output_data)} frames.")
        return output_data