import mediapipe as mp
import cv2
import requests
import os

# 1. Parameterized URL with Env Var override
# Default falls back to 'yalf' if not set in Render Dashboard
DEFAULT_BACKEND = "https://diamondmind-backend-yalf.onrender.com"
BACKEND_URL = os.environ.get("BACKEND_URL", DEFAULT_BACKEND)

# Standard MediaPipe 33-point topology connections
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5),
    (5, 6), (6, 8), (9, 10), (11, 12), (11, 13),
    (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
    (18, 20), (11, 23), (12, 24), (23, 24), (23, 25),
    (24, 26), (25, 27), (26, 28), (27, 29), (28, 30),
    (29, 31), (30, 32), (27, 31), (28, 32)
]

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
        except Exception as e:
            print(f"⚠️ Progress report failed: {e}")
            pass

    def _draw_overlay(self, image, landmarks):
        """Draws the skeleton overlay on the frame (ported from visualize.py)."""
        annotated_image = np.copy(image)
        h, w, _ = annotated_image.shape

        # 1. Draw Bones (Lines)
        for start_idx, end_idx in POSE_CONNECTIONS:
            start_point = landmarks.landmark[start_idx]
            end_point = landmarks.landmark[end_idx]
            
            x1, y1 = int(start_point.x * w), int(start_point.y * h)
            x2, y2 = int(end_point.x * w), int(end_point.y * h)
            
            # Green Line
            cv2.line(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 2. Draw Joints (Dots)
        for landmark in landmarks.landmark:
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            # Red Dot
            cv2.circle(annotated_image, (cx, cy), 4, (0, 0, 255), -1)

        return annotated_image

    def process_video(self, video_path, job_id=None):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        frame_count = 0
        frames = []
        valid_frames = 0

        # --- VIDEO WRITER SETUP ---
        # We save to /tmp so it's ephemeral but accessible by the service
        output_filename = f"analyzed_{job_id}.mp4" if job_id else "analyzed_output.mp4"
        output_path = os.path.join("/tmp", output_filename)
        
        # mp4v is widely supported for temp files; H.264 (avc1) might require extra libs
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        print(f"🎬 Starting processing: {video_path} (Job: {job_id})")
        print(f"💾 Saving visualization to: {output_path}")

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Convert BGR to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process
            results = self.pose.process(frame_rgb)
            
            timestamp_ms = (frame_count / fps) * 1000
            landmarks_array = None
            
            if results.pose_landmarks:
                valid_frames += 1
                
                # 1. Build JSON Data
                landmarks_array = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks_array.append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    })
                
                # 2. Draw Overlay for Video (using the helper)
                # Note: We draw on 'frame' (BGR) because OpenCV expects BGR for writing
                final_frame = self._draw_overlay(frame, results.pose_landmarks)
            else:
                # No skeleton detected? Just use original frame
                final_frame = frame

            # Write the frame to the output video
            out.write(final_frame)

            # Add to JSON list
            frames.append({
                "timestamp": timestamp_ms,
                "landmarks": landmarks_array
            })

            frame_count += 1

            if job_id and frame_count % 10 == 0:
                percent = (frame_count / total_frames) * 100
                self.report_progress(job_id, percent)

        cap.release()
        out.release()
        
        if job_id:
            self.report_progress(job_id, 100)
            
        print(f"✅ Complete. Processed {frame_count} frames.")
        
        return {
            "frames": frames,
            "total_frames": frame_count,
            "frames_with_person": valid_frames,
            "fps": fps,
            "video_filename": output_filename # 👈 Client needs this to request download
        }