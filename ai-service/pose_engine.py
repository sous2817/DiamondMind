import mediapipe as mp
import cv2
import requests
import os

# Hardcoded Backend URL (Tribal Knowledge: Service-to-Service wiring)
# In production, this should be an env var, but we'll lock it here for stability.
BACKEND_URL = "https://diamondmind-backend-yalf.onrender.com"

class PoseExtractor:
    # RESTORED: model_complexity=1 (Standard) to ensure we detect the player.
    # 0 was too fast/dumb and likely caused the "missing overlay" by missing the person.
    def __init__(self, static_image_mode=False, model_complexity=1, min_detection_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )

    def report_progress(self, job_id, progress):
        """Sends a fire-and-forget progress update to the backend."""
        if not job_id:
            return
        try:
            url = f"{BACKEND_URL}/api/jobs/{job_id}/progress"
            requests.post(url, json={"progress": int(progress)}, timeout=1)
        except:
            # Ignore connection errors to keep processing alive
            pass

    def process_video(self, video_path, job_id=None):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        frame_count = 0
        output_data = []
        valid_frames = 0 # Counter for frames where we actually found a person

        print(f"🎬 Starting processing: {video_path} (Job: {job_id})")

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process
            results = self.pose.process(frame_rgb)
            
            frame_data = {
                "frame_index": frame_count,
                "timestamp_ms": cap.get(cv2.CAP_PROP_POS_MSEC),
                "landmarks": {}
            }

            if results.pose_landmarks:
                valid_frames += 1
                for idx, landmark in enumerate(results.pose_landmarks.landmark):
                    landmark_name = self.mp_pose.PoseLandmark(idx).name
                    frame_data["landmarks"][landmark_name] = {
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    }
            else:
                frame_data["landmarks"] = None 

            output_data.append(frame_data)
            frame_count += 1

            # Report progress every 10 frames (to avoid flooding the network)
            if job_id and frame_count % 10 == 0:
                percent = (frame_count / total_frames) * 100
                self.report_progress(job_id, percent)

        cap.release()
        
        # FINAL REPORT
        if job_id:
            self.report_progress(job_id, 100)
            
        print(f"✅ Complete. Processed {frame_count} frames.")
        print(f"👀 Detection Stats: Found person in {valid_frames}/{frame_count} frames.")
        
        return output_data