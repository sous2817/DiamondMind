import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pose_engine import PoseAnalyzer
import numpy as np
import os

# --- DEFINE SKELETON CONNECTIONS MANUALLY ---
# These pairs correspond to the standard 33-point MediaPipe Pose topology.
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5),
    (5, 6), (6, 8), (9, 10), (11, 12), (11, 13),
    (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
    (18, 20), (11, 23), (12, 24), (23, 24), (23, 25),
    (24, 26), (25, 27), (26, 28), (27, 29), (28, 30),
    (29, 31), (30, 32), (27, 31), (28, 32)
]

def draw_landmarks_on_image(rgb_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(rgb_image)

    # Loop through the detected poses (usually just one)
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        # 1. Draw the "Bones" (Lines)
        for start_idx, end_idx in POSE_CONNECTIONS:
            # Get the landmarks
            start_point = pose_landmarks[start_idx]
            end_point = pose_landmarks[end_idx]
            
            # Convert normalized coordinates (0-1) to pixel coordinates
            h, w, _ = annotated_image.shape
            x1, y1 = int(start_point.x * w), int(start_point.y * h)
            x2, y2 = int(end_point.x * w), int(end_point.y * h)
            
            # Draw Green Line
            cv2.line(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 2. Draw the "Joints" (Dots)
        for landmark in pose_landmarks:
            h, w, _ = annotated_image.shape
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            
            # Draw Red Dot
            cv2.circle(annotated_image, (cx, cy), 4, (0, 0, 255), -1)

    return annotated_image

def create_visual_output(input_path, output_path="output_test.mp4"):
    if not os.path.exists(input_path):
        print(f"Error: Could not find {input_path}")
        return

    print(f"🎥 Processing video: {input_path}")
    
    # Initialize our Engine
    analyzer = PoseAnalyzer()
    
    # Open Video
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Prepare Output Video Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_idx = 0
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        # 1. Prepare Image for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = int((frame_idx / fps) * 1000)
        
        # 2. Run Detection
        detection_result = analyzer.landmarker.detect_for_video(mp_image, timestamp_ms)
        
        # 3. Draw Overlay
        if detection_result.pose_landmarks:
            # We convert back to BGR for OpenCV saving
            annotated_frame = draw_landmarks_on_image(frame, detection_result)
            out.write(annotated_frame)
        else:
            # If no body found, just write the original frame
            out.write(frame)
            
        frame_idx += 1
        if frame_idx % 10 == 0:
            print(f"Processing frame {frame_idx}...", end='\r')

    cap.release()
    out.release()
    print(f"\n✅ Visualization saved to: {output_path}")

if __name__ == "__main__":
    create_visual_output("test.mp4")