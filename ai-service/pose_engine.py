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

# 3. Frame Skipping Configuration (DM-28)
# FRAME_SKIP=1 means process every frame (no skipping)
# FRAME_SKIP=2 means process every 2nd frame (50% reduction)
# FRAME_SKIP=3 means process every 3rd frame (67% reduction)
FRAME_SKIP = int(os.environ.get("FRAME_SKIP", "1"))  # Default: skip every other frame

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
        
        # Load YOLO v3 ONNX bat detector (DM-66 - Memory optimized)
        try:
            import onnxruntime as ort
            model_path = os.path.join(
                os.path.dirname(__file__), 
                "yolo-bat-detection/models/production/best.onnx"
            )
            
            if not os.path.exists(model_path):
                print(f"⚠️ YOLO model not found at {model_path}, using geometric fallback only")
                self.bat_detector = None
            else:
                # Configure ONNX session for optimal CPU performance
                sess_options = ort.SessionOptions()
                sess_options.intra_op_num_threads = 2  # Limit threads for Render free tier
                sess_options.inter_op_num_threads = 1
                sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                
                # Create ONNX inference session (CPU only for Render free tier)
                self.bat_detector = ort.InferenceSession(
                    model_path,
                    sess_options=sess_options,
                    providers=['CPUExecutionProvider']
                )
                self.bat_conf_threshold = float(os.environ.get("YOLO_CONF_THRESHOLD", "0.25"))
                print(f"✅ Loaded YOLO v3 ONNX bat detector (confidence >= {self.bat_conf_threshold})")
        except Exception as e:
            print(f"⚠️ Failed to load YOLO model: {e}. Using geometric fallback only.")
            self.bat_detector = None
        
        # Temporal smoothing buffer for bat positions (reduces jitter)
        self.bat_position_buffer = []

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

    def _detect_bat_yolo(self, frame, hand_landmarks=None):
        """
        Detects bat using YOLOv8 v3 ONNX model (DM-66 - Memory optimized).
        Tracks barrel end instead of center for better swing analysis.
        Returns normalized (x, y) coordinates + confidence or None.
        """
        # Check if YOLO model is available
        if self.bat_detector is None:
            return None
        
        h, w = frame.shape[:2]
        
        try:
            # Preprocess frame for YOLO ONNX input
            # YOLO expects (1, 3, 640, 640) - batch, channels, height, width
            import cv2
            
            # Resize and normalize
            img = cv2.resize(frame, (640, 640))
            img = img.transpose(2, 0, 1)  # HWC to CHW
            img = img.astype('float32') / 255.0  # Normalize to [0, 1]
            img = np.expand_dims(img, axis=0)  # Add batch dimension
            
            # Run ONNX inference
            input_name = self.bat_detector.get_inputs()[0].name
            outputs = self.bat_detector.run(None, {input_name: img})
            
            # Parse YOLO ONNX output
            # Output shape: (1, 5, 8400) for YOLOv8n with 1 class
            # 5 = cx, cy, w, h, confidence
            predictions = outputs[0][0]  # Remove batch dimension -> (5, 8400)
            
            # Get confidence scores (last row)
            confidences = predictions[4, :]
            
            # Find detections above threshold
            valid_mask = confidences >= self.bat_conf_threshold
            if not valid_mask.any():
                return None
            
            # Get best detection (highest confidence)
            best_idx = np.argmax(confidences)
            if confidences[best_idx] < self.bat_conf_threshold:
                return None
            
            # Extract bounding box (normalized to 640x640)
            cx_norm = predictions[0, best_idx]  # center x (0-640)
            cy_norm = predictions[1, best_idx]  # center y (0-640)
            w_norm = predictions[2, best_idx]   # width
            h_norm = predictions[3, best_idx]   # height
            
            # Calculate bounding box corners
            x1_norm = cx_norm - w_norm / 2
            y1_norm = cy_norm - h_norm / 2
            x2_norm = cx_norm + w_norm / 2
            y2_norm = cy_norm + h_norm / 2
            
            # Convert to original frame coordinates
            x1 = x1_norm * w / 640
            y1 = y1_norm * h / 640
            x2 = x2_norm * w / 640
            y2 = y2_norm * h / 640
            cx = cx_norm * w / 640
            cy = cy_norm * h / 640
            
            # Determine barrel position using hand landmarks
            bat_x, bat_y = cx, cy  # Default to center if hands not detected
            
            if hand_landmarks and hasattr(hand_landmarks, 'landmark'):
                try:
                    # Get average hand position (wrists)
                    left_wrist = hand_landmarks.landmark[15]  # Left wrist
                    right_wrist = hand_landmarks.landmark[16]  # Right wrist
                    hand_x = ((left_wrist.x + right_wrist.x) / 2) * w
                    hand_y = ((left_wrist.y + right_wrist.y) / 2) * h
                    
                    # Calculate distances from hands to each corner of the box
                    # The handle is the end closest to hands, barrel is the opposite
                    corners = [
                        (x1, y1),  # Top-left
                        (x2, y1),  # Top-right
                        (x1, y2),  # Bottom-left
                        (x2, y2),  # Bottom-right
                    ]
                    
                    distances = [
                        ((corner[0] - hand_x)**2 + (corner[1] - hand_y)**2)**0.5
                        for corner in corners
                    ]
                    
                    # Find closest corner (handle end)
                    handle_idx = distances.index(min(distances))
                    handle_corner = corners[handle_idx]
                    
                    # Barrel is the opposite corner
                    # 0->3, 1->2, 2->1, 3->0
                    barrel_idx = 3 - handle_idx
                    barrel_corner = corners[barrel_idx]
                    
                    # Track the barrel corner
                    bat_x, bat_y = barrel_corner
                    
                except Exception as e:
                    # If hand tracking fails, fall back to center
                    print(f"⚠️ Hand landmark processing failed: {e}, using bbox center")
                    bat_x, bat_y = cx, cy
            
            # Apply temporal smoothing
            smoothed_x, smoothed_y = self._smooth_bat_position(int(bat_x), int(bat_y))
            
            # Return normalized coordinates with confidence
            return {
                "x": round(smoothed_x / w, 4),
                "y": round(smoothed_y / h, 4),
                "confidence": round(float(confidences[best_idx]), 3)
            }
        except Exception as e:
            print(f"⚠️ YOLO detection error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _detect_bat_geometric(self, frame, hand_landmarks=None):
        """
        LEGACY: Detects bat position using GEOMETRIC approach (no color detection).
        Returns normalized (x, y) coordinates or None if bat not detected.
        
        NOTE: This is a fallback method. Will be removed after YOLO testing is complete.
        
        Strategy:
        1. Use hand landmarks (15=left wrist, 16=right wrist) as anchor points
        2. Calculate bat direction vector from hand positions
        3. Extend along this vector to estimate bat barrel position
        
        This approach:
        - Doesn't rely on color/HSV (works with any bat color)
        - 100% detection rate (works whenever pose is detected)
        - Fast (no contour processing)
        - Accurate (bat always extends from hands)
        """
        h, w = frame.shape[:2]
        
        # Require hand landmarks for geometric approach
        if not hand_landmarks:
            return None
        
        # Get hand positions
        left_wrist = hand_landmarks.landmark[15]
        right_wrist = hand_landmarks.landmark[16]
        
        left_x, left_y = int(left_wrist.x * w), int(left_wrist.y * h)
        right_x, right_y = int(right_wrist.x * w), int(right_wrist.y * h)
        
        # Calculate grip position (midpoint between hands)
        grip_x = (left_x + right_x) // 2
        grip_y = (left_y + right_y) // 2
        
        # Calculate bat direction vector (from left to right hand)
        bat_dx = right_x - left_x
        bat_dy = right_y - left_y
        
        # Calculate hand distance
        hand_distance = np.sqrt(bat_dx**2 + bat_dy**2)
        
        # If hands are too close together, can't determine bat direction
        if hand_distance < 20:  # Minimum 20 pixels apart
            return None
        
        # Normalize the direction vector
        bat_dx_norm = bat_dx / hand_distance
        bat_dy_norm = bat_dy / hand_distance
        
        # Extend along bat direction to estimate barrel position
        # Typical bat is ~34 inches, hands are ~12 inches apart
        # So extend 2.5x the hand distance
        extension = hand_distance * 2.5
        
        barrel_x = grip_x + int(bat_dx_norm * extension)
        barrel_y = grip_y + int(bat_dy_norm * extension)
        
        # Clamp to frame boundaries
        barrel_x = max(0, min(w - 1, barrel_x))
        barrel_y = max(0, min(h - 1, barrel_y))
        
        # Apply temporal smoothing to reduce jitter
        smoothed_x, smoothed_y = self._smooth_bat_position(barrel_x, barrel_y)
        
        # Return normalized coordinates (no confidence for geometric)
        return {
            "x": round(smoothed_x / w, 4),
            "y": round(smoothed_y / h, 4)
        }
    
    def _detect_bat(self, frame, hand_landmarks=None):
        """
        Primary bat detection method with YOLO + geometric fallback.
        
        Strategy:
        1. Try YOLO first (ML-based, production quality)
           - Uses hand landmarks to track barrel end if available
        2. Fallback to geometric if YOLO fails (hand-based estimation)
        
        Returns normalized (x, y) coordinates with optional confidence.
        """
        # Try YOLO first (pass hand landmarks for barrel tracking)
        yolo_result = self._detect_bat_yolo(frame, hand_landmarks)
        if yolo_result is not None:
            return yolo_result
        
        # Fallback to geometric (legacy)
        if hand_landmarks:
            return self._detect_bat_geometric(frame, hand_landmarks)
        
        return None
    
    def _smooth_bat_position(self, x, y, buffer_size=5):
        """
        Apply temporal smoothing to bat position using a rolling average.
        Reduces jitter from frame-to-frame hand position changes.
        """
        # Add current position to buffer
        self.bat_position_buffer.append((x, y))
        
        # Keep only last N positions
        if len(self.bat_position_buffer) > buffer_size:
            self.bat_position_buffer.pop(0)
        
        # Calculate average position
        if len(self.bat_position_buffer) > 0:
            avg_x = sum(pos[0] for pos in self.bat_position_buffer) / len(self.bat_position_buffer)
            avg_y = sum(pos[1] for pos in self.bat_position_buffer) / len(self.bat_position_buffer)
            return int(avg_x), int(avg_y)
        
        return x, y
    
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

            frame_count += 1  # Increment BEFORE skip check
            timestamp_ms = ((frame_count - 1) / fps) * 1000  # Adjust for 0-indexed
            
            # DM-28: Frame skipping logic
            # Always process first frame and last frame
            is_first_frame = (frame_count == 1)
            is_last_frame = (frame_count >= total_frames)
            should_process = (frame_count % FRAME_SKIP == 0) or is_first_frame or is_last_frame
            
            if not should_process:
                # Skip processing, but still write frame to output video
                out.write(frame)
                
                # Add placeholder to JSON with null landmarks
                frames.append({
                    "timestamp": timestamp_ms,
                    "landmarks": None,  # Skipped frame
                    "bat_position": None
                })
                
                # Report progress even for skipped frames
                if job_id and frame_count % 10 == 0:
                    percent = (frame_count / total_frames) * 100
                    self.report_progress(job_id, percent)
                
                continue
            
            # Process frame (only for non-skipped frames)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            
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
                
                # 2. Detect Bat Position (YOLO + geometric fallback)
                bat_position = self._detect_bat(frame, results.pose_landmarks)
                
                # 3. Draw Overlay
                final_frame = self._draw_overlay(frame, results.pose_landmarks)
            else:
                # No person detected, still try bat detection (YOLO only, no landmarks)
                bat_position = self._detect_bat(frame)
                final_frame = frame

            # Write frame to video
            out.write(final_frame)

            # Add to JSON list
            frames.append({
                "timestamp": timestamp_ms,
                "landmarks": landmarks_array,
                "bat_position": bat_position
            })

            # Report progress
            if job_id and frame_count % 10 == 0:
                percent = (frame_count / total_frames) * 100
                self.report_progress(job_id, percent)

            if frame_count % 50 == 0:
                processed_count = sum(1 for f in frames if f["landmarks"] is not None)
                print(f"   ...Read {frame_count}/{total_frames} frames, Processed {processed_count} ({timestamp_ms:.0f}ms)")

        cap.release()
        out.release()
        
        if job_id:
            self.report_progress(job_id, 100)
            
        print(f"✅ Complete. Processed {frame_count} frames.")
        
        # Calculate processed frames count
        processed_frames = sum(1 for f in frames if f["landmarks"] is not None)
        
        return {
            "frames": frames,
            "total_frames": frame_count,
            "frames_processed": processed_frames,  # DM-28: How many actually processed
            "frames_with_person": valid_frames,
            "fps": fps,
            "video_filename": output_filename,
            "frame_skip": FRAME_SKIP  # DM-28: Document skip rate used
        }