"""
Text-based diagnostic - outputs analysis as text instead of images.
"""
import cv2
import numpy as np
import sys

BAT_HSV_LOWER = [0, 0, 0]
BAT_HSV_UPPER = [180, 255, 50]

def analyze_frame_text(video_path, frame_num=50):
    """Analyzes a specific frame and outputs text diagnostics."""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Video Info:")
    print(f"   Resolution: {width}x{height}")
    print(f"   Total frames: {total_frames}")
    print(f"   FPS: {fps:.2f}")
    print(f"\n🎨 HSV Range: [{BAT_HSV_LOWER[0]}, {BAT_HSV_LOWER[1]}, {BAT_HSV_LOWER[2]}] to [{BAT_HSV_UPPER[0]}, {BAT_HSV_UPPER[1]}, {BAT_HSV_UPPER[2]}]")
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    
    if not ret:
        print(f"❌ Could not read frame {frame_num}")
        return
    
    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_bound = np.array(BAT_HSV_LOWER)
    upper_bound = np.array(BAT_HSV_UPPER)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Morphological operations
    kernel = np.ones((5, 5), np.uint8)
    mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"\n📊 Frame {frame_num} Analysis:")
    print(f"   Total contours found: {len(contours)}")
    
    # Filter and analyze contours
    min_area = 800
    valid_contours = []
    
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        
        # Check aspect ratio
        rect = cv2.minAreaRect(c)
        box_width, box_height = rect[1]
        if box_width == 0 or box_height == 0:
            continue
        
        aspect_ratio = max(box_width, box_height) / min(box_width, box_height)
        
        # Calculate centroid
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            valid_contours.append({
                'id': i,
                'area': area,
                'aspect_ratio': aspect_ratio,
                'centroid': (cx, cy),
                'is_elongated': aspect_ratio > 3.0
            })
    
    print(f"   Valid contours (area > {min_area}): {len(valid_contours)}")
    
    if valid_contours:
        print(f"\n   Top 5 Contours:")
        sorted_contours = sorted(valid_contours, key=lambda x: x['area'], reverse=True)[:5]
        for i, cont in enumerate(sorted_contours, 1):
            elongated_mark = "🏏 ELONGATED" if cont['is_elongated'] else "❌ Not elongated"
            print(f"   {i}. Area: {int(cont['area'])}px | Aspect: {cont['aspect_ratio']:.2f} | Pos: ({cont['centroid'][0]}, {cont['centroid'][1]}) | {elongated_mark}")
        
        # Check which would be selected
        elongated_contours = [c for c in valid_contours if c['is_elongated']]
        if elongated_contours:
            selected = max(elongated_contours, key=lambda x: x['area'])
            print(f"\n   ✅ SELECTED (largest elongated): Area={int(selected['area'])}px, Aspect={selected['aspect_ratio']:.2f}, Pos={selected['centroid']}")
        else:
            print(f"\n   ⚠️  NO ELONGATED CONTOURS FOUND (aspect ratio > 3.0)")
            print(f"   This means no bat-shaped objects were detected!")
    else:
        print(f"\n   ❌ NO VALID CONTOURS FOUND")
        print(f"   Possible reasons:")
        print(f"   - Bat color doesn't match HSV range")
        print(f"   - Bat is too small (< {min_area}px)")
        print(f"   - Bat is not visible in this frame")
    
    cap.release()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python text_diagnostic.py <video_path> [frame_number]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    frame_num = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    analyze_frame_text(video_path, frame_num)
