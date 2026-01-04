"""
Test the actual hand-anchored bat detection with MediaPipe pose.
This simulates what the deployed code does.
"""
import cv2
import mediapipe as mp
import sys

# Import from pose_engine
import sys
sys.path.insert(0, '.')
from pose_engine import PoseExtractor

def test_full_pipeline(video_path, sample_frames=[50, 100, 150, 200]):
    """Test the complete pipeline with pose + bat detection."""
    
    extractor = PoseExtractor()
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"📹 Video: {video_path}")
    print(f"   Total frames: {total_frames}, FPS: {fps:.2f}")
    print(f"\n🧪 Testing Hand-Anchored Bat Detection:\n")
    
    bat_detected_count = 0
    
    for frame_num in sample_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        
        if not ret:
            continue
        
        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose
        results = extractor.pose.process(frame_rgb)
        
        print(f"Frame {frame_num}:")
        
        if results.pose_landmarks:
            # Get hand positions
            left_hand = results.pose_landmarks.landmark[15]
            right_hand = results.pose_landmarks.landmark[16]
            h, w = frame.shape[:2]
            
            left_x, left_y = int(left_hand.x * w), int(left_hand.y * h)
            right_x, right_y = int(right_hand.x * w), int(right_hand.y * h)
            grip_x = (left_x + right_x) // 2
            grip_y = (left_y + right_y) // 2
            
            print(f"  ✅ Pose detected")
            print(f"  👐 Grip position: ({grip_x}, {grip_y})")
            
            # Detect bat
            bat_pos = extractor._detect_bat_hsv(frame, results.pose_landmarks)
            
            if bat_pos:
                bat_x = int(bat_pos['x'] * w)
                bat_y = int(bat_pos['y'] * h)
                print(f"  🏏 BAT DETECTED at ({bat_x}, {bat_y})")
                bat_detected_count += 1
            else:
                print(f"  ❌ No bat detected (no elongated objects found near hands)")
        else:
            print(f"  ❌ No pose detected")
        
        print()
    
    cap.release()
    
    detection_rate = (bat_detected_count / len(sample_frames)) * 100
    print(f"\n📊 Detection Rate: {bat_detected_count}/{len(sample_frames)} frames ({detection_rate:.0f}%)")
    
    if detection_rate < 50:
        print(f"\n⚠️  LOW DETECTION RATE!")
        print(f"Possible causes:")
        print(f"  - Bat color doesn't match HSV range [0,0,0] to [180,255,50]")
        print(f"  - Bat is too small or too large")
        print(f"  - Bat aspect ratio < 3.0 (not elongated enough)")
        print(f"  - Bat is outside the search region (30% of frame around hands)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_full_pipeline.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    test_full_pipeline(video_path)
