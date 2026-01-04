"""
Diagnostic script to visualize bat detection and identify issues.
Run this on a test video to see what the HSV detection is actually tracking.
"""
import cv2
import numpy as np
import sys

# Default HSV ranges from pose_engine.py
BAT_HSV_LOWER = [0, 0, 0]      # Black bat default
BAT_HSV_UPPER = [180, 255, 50]

def visualize_bat_detection(video_path):
    """
    Shows side-by-side view of:
    1. Original frame
    2. HSV mask (what's being detected)
    3. Detected contours with centroids
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return
    
    print("Controls:")
    print("  SPACE - Pause/Resume")
    print("  Q - Quit")
    print("  S - Save current frame analysis")
    print("\nHSV Range:")
    print(f"  Lower: {BAT_HSV_LOWER}")
    print(f"  Upper: {BAT_HSV_UPPER}")
    
    paused = False
    frame_count = 0
    
    while cap.isOpened():
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask
        lower_bound = np.array(BAT_HSV_LOWER)
        upper_bound = np.array(BAT_HSV_UPPER)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by area
        min_area = 500
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        # Draw on visualization frame
        vis_frame = frame.copy()
        
        # Draw all valid contours in blue
        cv2.drawContours(vis_frame, valid_contours, -1, (255, 0, 0), 2)
        
        # Find and highlight largest contour (what gets selected)
        if valid_contours:
            largest_contour = max(valid_contours, key=cv2.contourArea)
            cv2.drawContours(vis_frame, [largest_contour], -1, (0, 255, 0), 3)
            
            # Draw centroid
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(vis_frame, (cx, cy), 10, (0, 255, 255), -1)  # Yellow dot
                
                # Add text with area
                area = cv2.contourArea(largest_contour)
                cv2.putText(vis_frame, f"Area: {int(area)}", (cx + 15, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # Add frame info
        cv2.putText(vis_frame, f"Frame: {frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(vis_frame, f"Contours: {len(valid_contours)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Create side-by-side display
        mask_colored = cv2.cvtColor(mask_cleaned, cv2.COLOR_GRAY2BGR)
        combined = np.hstack([frame, mask_colored, vis_frame])
        
        # Resize for display
        scale = 0.5
        h, w = combined.shape[:2]
        combined_resized = cv2.resize(combined, (int(w * scale), int(h * scale)))
        
        cv2.imshow('Bat Detection Debug (Original | Mask | Detection)', combined_resized)
        
        key = cv2.waitKey(30 if not paused else 0) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('s'):
            cv2.imwrite(f'debug_frame_{frame_count}.jpg', combined)
            print(f"Saved debug_frame_{frame_count}.jpg")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_bat_detection.py <video_path>")
        print("Example: python debug_bat_detection.py ../backend/uploads/bat_tracker1.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    visualize_bat_detection(video_path)
