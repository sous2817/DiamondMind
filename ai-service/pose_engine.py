import mediapipe as mp
import cv2
import requests
import os
import numpy as np

# 1. Parameterized URL with Env Var override
DEFAULT_BACKEND = "https://diamondmind-backend-yalf.onrender.com"
BACKEND_URL = os.environ.get("BACKEND_URL", DEFAULT_BACKEND)

# 2. Bat Detection HSV Configuration (Environment Variables)
# Default values work for black/dark bats. Adjust for different colors:
# Red bats: [0, 100, 100] to [10, 255, 255]
# Blue bats: [100, 100, 100] to [130, 255, 255]
# Black bats: [0, 0, 0] to [180, 255, 50]
BAT_HSV_LOWER = list(map(int, os.environ.get("BAT_HSV_LOWER", "0,0,0").split(",")))
BAT_HSV_UPPER = list(map(int, os.environ.get("BAT_HSV_UPPER", "180,255,50").split(",")))

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

    def _detect_bat_hsv(self, frame, hand_landmarks=None):
        """
        Detects bat position using hand-anchored approach.
        Returns normalized (x, y) coordinates or None if bat not detected.
        
        Strategy:
        1. Use hand landmarks as anchor points (most reliable)
        2. Search for elongated objects extending from hands
        3. Estimate bat barrel position along the extension vector
        """
        h, w = frame.shape[:2]
        
        # If no hand landmarks, fall back to basic color detection
        if not hand_landmarks:
            return self._detect_bat_color_only(frame)
        
        # Get both hand positions
        left_hand = hand_landmarks.landmark[15]   # Left wrist
        right_hand = hand_landmarks.landmark[16]  # Right wrist
        
        left_x, left_y = int(left_hand.x * w), int(left_hand.y * h)
        right_x, right_y = int(right_hand.x * w), int(right_hand.y * h)
        
        # Calculate midpoint between hands (grip position)
        grip_x = (left_x + right_x) // 2
        grip_y = (left_y + right_y) // 2
        
        # Create search region around hands (expanded area)
        search_radius = int(max(w, h) * 0.4)  # 40% of frame dimension
        x1 = max(0, grip_x - search_radius)
        y1 = max(0, grip_y - search_radius)
        x2 = min(w, grip_x + search_radius)
        y2 = min(h, grip_y + search_radius)
        
        # Extract search region
        search_region = frame[y1:y2, x1:x2]
        
        if search_region.size == 0:
            return None
        
        # Convert to HSV and create mask
        hsv = cv2.cvtColor(search_region, cv2.COLOR_BGR2HSV)
        lower_bound = np.array(BAT_HSV_LOWER)
        upper_bound = np.array(BAT_HSV_UPPER)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours in search region
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Filter for elongated objects (bats are long and thin)
        min_area = 800
        max_area = (x2 - x1) * (y2 - y1) * 0.15  # Max 15% of search region
        
        bat_candidates = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < min_area or area > max_area:
                continue
            
            # Check aspect ratio
            rect = cv2.minAreaRect(c)
            box_width, box_height = rect[1]
            if box_width == 0 or box_height == 0:
                continue
            
            aspect_ratio = max(box_width, box_height) / min(box_width, box_height)
            
            # Bats should be elongated (aspect ratio > 3)
            if aspect_ratio > 3.0:
                # Calculate distance from grip point
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Convert to frame coordinates
                    cx_frame = cx + x1
                    cy_frame = cy + y1
                    
                    dist_from_grip = ((cx_frame - grip_x) ** 2 + (cy_frame - grip_y) ** 2) ** 0.5
                    
                    bat_candidates.append({
                        'contour': c,
                        'centroid': (cx_frame, cy_frame),
                        'distance': dist_from_grip,
                        'aspect_ratio': aspect_ratio
                    })
        
        if not bat_candidates:
            return None
        
        # Select best candidate: prefer elongated objects near hands
        # Weight: closer to hands = better, higher aspect ratio = better
        def score_candidate(candidate):
            # Normalize distance (closer = higher score)
            max_dist = search_radius
            dist_score = 1.0 - (candidate['distance'] / max_dist)
            
            # Normalize aspect ratio (more elongated = higher score)
            aspect_score = min(candidate['aspect_ratio'] / 10.0, 1.0)
            
            # Combined score (distance weighted more heavily)
            return (dist_score * 0.7) + (aspect_score * 0.3)
        
        best_candidate = max(bat_candidates, key=score_candidate)
        cx_frame, cy_frame = best_candidate['centroid']
        
        # Estimate bat barrel position (extend from grip along bat direction)
        # The centroid is roughly mid-bat, barrel is farther from hands
        dx = cx_frame - grip_x
        dy = cy_frame - grip_y
        
        # Extend 1.5x to approximate barrel position
        barrel_x = grip_x + int(dx * 1.5)
        barrel_y = grip_y + int(dy * 1.5)
        
        # Clamp to frame boundaries
        barrel_x = max(0, min(w - 1, barrel_x))
        barrel_y = max(0, min(h - 1, barrel_y))
        
        # Return normalized coordinates
        return {
            "x": round(barrel_x / w, 4),
            "y": round(barrel_y / h, 4)
        }
    
    def _detect_bat_color_only(self, frame):
        """
        Fallback: Basic color detection without hand landmarks.
        Used when pose detection fails.
        """
        h, w = frame.shape[:2]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower_bound = np.array(BAT_HSV_LOWER)
        upper_bound = np.array(BAT_HSV_UPPER)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find largest elongated contour
        valid_contours = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < 1000:
                continue
            
            rect = cv2.minAreaRect(c)
            box_width, box_height = rect[1]
            if box_width == 0 or box_height == 0:
                continue
            
            aspect_ratio = max(box_width, box_height) / min(box_width, box_height)
            if aspect_ratio > 3.0:
                valid_contours.append(c)
        
        if not valid_contours:
            return None
        
        bat_contour = max(valid_contours, key=cv2.contourArea)
        M = cv2.moments(bat_contour)
        
        if M["m00"] == 0:
            return None
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        return {
            "x": round(cx / w, 4),
            "y": round(cy / h, 4)
        }

    def _draw_overlay(self, image, landmarks):
        """Draws the skeleton overlay on the frame."""
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

    def process_video(self, video_path, job_id=None, output_dir=None):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Use system temp dir if no output_dir provided
        if output_dir is None:
            import tempfile
            output_dir = tempfile.gettempdir()

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        frame_count = 0
        frames = []
        valid_frames = 0

        # --- VIDEO WRITER SETUP ---
        output_filename = f"analyzed_{job_id}.mp4" if job_id else "analyzed_output.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        # mp4v is safe for Windows; if it fails, try 'avc1'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        print(f"🎬 Starting processing: {video_path} (Job: {job_id})")
        print(f"💾 Saving visualization to: {output_path}")

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process Pose
            results = self.pose.process(frame_rgb)
            
            timestamp_ms = (frame_count / fps) * 1000
            landmarks_array = None
            bat_position = None
            
            if results.pose_landmarks:
                valid_frames += 1
                
                # 1. Build JSON Data for Landmarks
                landmarks_array = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks_array.append({
                        "x": round(landmark.x, 4),
                        "y": round(landmark.y, 4),
                        "z": round(landmark.z, 4),
                        "visibility": round(landmark.visibility, 4)
                    })
                
                # 2. Detect Bat Position (HSV-based)
                bat_position = self._detect_bat_hsv(frame, results.pose_landmarks)
                
                # 3. Draw Overlay
                final_frame = self._draw_overlay(frame, results.pose_landmarks)
            else:
                # No person detected, still try bat detection
                bat_position = self._detect_bat_hsv(frame)
                final_frame = frame

            # Write frame to video
            out.write(final_frame)

            # Add to JSON list
            frames.append({
                "timestamp": timestamp_ms,
                "landmarks": landmarks_array,
                "bat_position": bat_position
            })

            frame_count += 1

            if job_id and frame_count % 10 == 0:
                percent = (frame_count / total_frames) * 100
                self.report_progress(job_id, percent)

            if frame_count % 50 == 0:
                print(f"   ...Processed {frame_count}/{total_frames} frames ({timestamp_ms:.0f}ms)")

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
            "video_filename": output_filename
        }