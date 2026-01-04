"""
Headless diagnostic script - saves diagnostic images instead of displaying them.
Analyzes bat detection and saves frames showing what's being detected.
"""
import cv2
import numpy as np
import sys
import os

# Default HSV ranges from pose_engine.py
BAT_HSV_LOWER = [0, 0, 0]      # Black bat default
BAT_HSV_UPPER = [180, 255, 50]

def analyze_bat_detection(video_path, output_dir="debug_output"):
    """
    Analyzes bat detection and saves diagnostic images.
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"📹 Video: {video_path}")
    print(f"   Total frames: {total_frames}")
    print(f"   FPS: {fps}")
    print(f"\n🎨 HSV Range:")
    print(f"   Lower: {BAT_HSV_LOWER}")
    print(f"   Upper: {BAT_HSV_UPPER}")
    print(f"\n📊 Analyzing frames...")
    
    # Sample frames at intervals
    sample_frames = [10, 30, 50, 70, 90]  # Frame numbers to analyze
    
    for frame_num in sample_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        
        if not ret:
            continue
        
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
        for i, contour in enumerate(valid_contours):
            area = cv2.contourArea(contour)
            cv2.drawContours(vis_frame, [contour], -1, (255, 0, 0), 2)
            
            # Label each contour with its area
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.putText(vis_frame, f"#{i+1}: {int(area)}px", (cx, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # Find and highlight largest contour (what gets selected)
        if valid_contours:
            largest_contour = max(valid_contours, key=cv2.contourArea)
            cv2.drawContours(vis_frame, [largest_contour], -1, (0, 255, 0), 3)
            
            # Draw centroid (yellow - this is what shows in the app)
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(vis_frame, (cx, cy), 15, (0, 255, 255), -1)  # Yellow dot
                
                area = cv2.contourArea(largest_contour)
                cv2.putText(vis_frame, f"SELECTED: {int(area)}px", (cx + 20, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Add frame info
        cv2.putText(vis_frame, f"Frame: {frame_num}/{total_frames}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(vis_frame, f"Valid Contours: {len(valid_contours)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Create side-by-side display
        mask_colored = cv2.cvtColor(mask_cleaned, cv2.COLOR_GRAY2BGR)
        combined = np.hstack([frame, mask_colored, vis_frame])
        
        # Save diagnostic image
        output_path = os.path.join(output_dir, f"frame_{frame_num:04d}_analysis.jpg")
        cv2.imwrite(output_path, combined)
        print(f"   ✅ Saved: {output_path} ({len(valid_contours)} contours)")
    
    cap.release()
    print(f"\n✅ Analysis complete! Check {output_dir}/ for diagnostic images")
    print(f"\n💡 Interpretation:")
    print(f"   - LEFT: Original frame")
    print(f"   - MIDDLE: HSV mask (white = detected)")
    print(f"   - RIGHT: Detection (blue = all contours, green = selected, yellow = centroid)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_bat_detection.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    analyze_bat_detection(video_path)
