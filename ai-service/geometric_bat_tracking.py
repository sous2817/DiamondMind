"""
GEOMETRIC BAT TRACKING - No color detection needed!

Strategy:
1. Use hand landmarks (15, 16) to determine bat grip
2. Calculate bat direction from hand positions
3. Extend along this direction to estimate bat barrel
4. Track this geometric estimate through the swing

This approach:
- Doesn't rely on color detection (no HSV issues)
- Works with any bat color
- Uses only reliable pose landmarks
- Much faster (no contour processing)
"""
import cv2
import numpy as np
import mediapipe as mp
import sys

def geometric_bat_tracking(video_path, sample_frames=[30, 60, 90, 120]):
    """Test geometric bat tracking approach."""
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"📹 Video: {total_frames} frames @ {fps:.2f} FPS")
    print(f"\n🧪 Testing Geometric Bat Tracking (No Color Detection):\n")
    
    for frame_num in sample_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        
        if not ret:
            continue
        
        h, w = frame.shape[:2]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        
        print(f"Frame {frame_num}:")
        
        if results.pose_landmarks:
            # Get hand positions
            left_wrist = results.pose_landmarks.landmark[15]
            right_wrist = results.pose_landmarks.landmark[16]
            
            left_x, left_y = int(left_wrist.x * w), int(left_wrist.y * h)
            right_x, right_y = int(right_wrist.x * w), int(right_wrist.y * h)
            
            # Grip position (midpoint)
            grip_x = (left_x + right_x) // 2
            grip_y = (left_y + right_y) // 2
            
            # Bat direction vector (from left to right hand)
            bat_dx = right_x - left_x
            bat_dy = right_y - left_y
            
            # Normalize the vector
            bat_length = np.sqrt(bat_dx**2 + bat_dy**2)
            if bat_length > 0:
                bat_dx_norm = bat_dx / bat_length
                bat_dy_norm = bat_dy / bat_length
                
                # Extend 2.5x the hand distance to estimate bat barrel
                # (typical bat is ~34 inches, hands are ~12 inches apart)
                extension = bat_length * 2.5
                
                barrel_x = grip_x + int(bat_dx_norm * extension)
                barrel_y = grip_y + int(bat_dy_norm * extension)
                
                # Clamp to frame
                barrel_x = max(0, min(w - 1, barrel_x))
                barrel_y = max(0, min(h - 1, barrel_y))
                
                print(f"  👐 Hands: L({left_x},{left_y}) R({right_x},{right_y})")
                print(f"  ✊ Grip: ({grip_x}, {grip_y})")
                print(f"  🏏 Bat barrel (geometric): ({barrel_x}, {barrel_y})")
                print(f"  📏 Hand distance: {int(bat_length)}px, Extension: {int(extension)}px")
            else:
                print(f"  ⚠️  Hands too close together")
        else:
            print(f"  ❌ No pose detected")
        
        print()
    
    cap.release()
    pose.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python geometric_bat_tracking.py <video_path>")
        sys.exit(1)
    
    geometric_bat_tracking(sys.argv[1])
