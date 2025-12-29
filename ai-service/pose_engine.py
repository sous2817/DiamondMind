import mediapipe as mp
import cv2
import requests
import os

# 1. Parameterized URL with Env Var override
# Default falls back to 'yalf' if not set in Render Dashboard
DEFAULT_BACKEND = "https://diamondmind-backend-yalf.onrender.com"
BACKEND_URL = os.environ.get("BACKEND_URL", DEFAULT_BACKEND)

class PoseExtractor:
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
            print(f"📊 Progress reported: {int(progress)}%")
        except Exception as e:
            # Ignore connection errors to keep processing alive
            print(f"⚠️ Progress report failed: {e}")
            pass

    def process_video(self, video_path, job_id=None):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Fallback to 30fps if not detected
        frame_count = 0
        frames = []  # Changed from output_data to match mobile app's expected key
        valid_frames = 0

        print(f"🎬 Starting processing: {video_path} (Job: {job_id})")
        print(f"📹 Video info: {total_frames} frames, {fps} fps")
        print(f"📡 Reporting progress to: {BACKEND_URL}")

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process
            results = self.pose.process(frame_rgb)
            
            # Calculate timestamp in milliseconds
            timestamp_ms = (frame_count / fps) * 1000
            
            # 🔧 FIX: Build landmarks as an ARRAY (not a dict)
            landmarks_array = None
            
            if results.pose_landmarks:
                valid_frames += 1
                # MediaPipe returns 33 landmarks (0-32)
                landmarks_array = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks_array.append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    })
            
            # 🔧 FIX: Use the exact keys the mobile app expects
            frame_data = {
                "timestamp": timestamp_ms,  # Changed from timestamp_ms
                "landmarks": landmarks_array  # Now an array or None
            }

            frames.append(frame_data)
            frame_count += 1

            # Report progress every 10 frames
            if job_id and frame_count % 10 == 0:
                percent = (frame_count / total_frames) * 100
                self.report_progress(job_id, percent)

        cap.release()
        
        # FINAL REPORT
        if job_id:
            self.report_progress(job_id, 100)
            
        print(f"✅ Complete. Processed {frame_count} frames.")
        print(f"👀 Detection Stats: Found person in {valid_frames}/{frame_count} frames.")
        
        if valid_frames == 0:
            print("⚠️ WARNING: No person detected in any frame! Check video quality/lighting.")
        
        # 🔧 FIX: Return the structure the mobile app expects
        return {
            "frames": frames,
            "total_frames": frame_count,
            "frames_with_person": valid_frames,
            "fps": fps
        }