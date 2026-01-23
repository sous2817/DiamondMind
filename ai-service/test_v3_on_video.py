"""
Test YOLOv8 v3 Model on Real Video
Compare with v2.5 results
"""

from ultralytics import YOLO
import cv2
from pathlib import Path
import sys

# Configuration
MODEL_PATH = "yolo-bat-detection/models/v3_full_5329imgs/best.pt"
CONF_THRESHOLD = 0.05  # Standard confidence threshold

# Get video path from command line argument
if len(sys.argv) < 2:
    print("Usage: python test_v3_on_video.py <video_path>")
    print("Example: python test_v3_on_video.py C:/videos/bat1.mp4")
    sys.exit(1)

# Join all args to handle paths with spaces (e.g., "G:\My Drive\...")
VIDEO_PATH = " ".join(sys.argv[1:])
video_name = Path(VIDEO_PATH).stem
OUTPUT_DIR = Path("C:/dm/docs/test-videos/v3_predictions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("🏏 Testing YOLOv8 v3 Model")
print("=" * 50)
print(f"Model: {MODEL_PATH}")
print(f"Video: {VIDEO_PATH}")
print(f"Output: {OUTPUT_DIR}")
print(f"Confidence: {CONF_THRESHOLD}")
print("=" * 50)

# Load model
model = YOLO(MODEL_PATH)

# Run inference 
results = model.predict(
    source=VIDEO_PATH,
    conf=CONF_THRESHOLD,
    save=True,
    project=str(OUTPUT_DIR),
    name=video_name,
    exist_ok=True,
    verbose=True
)

# Count detections
total_frames = len(results)
frames_with_detections = sum(1 for r in results if len(r.boxes) > 0)
total_detections = sum(len(r.boxes) for r in results)

print("\n" + "=" * 50)
print("📊 Detection Summary")
print("=" * 50)
print(f"Total frames: {total_frames}")
print(f"Frames with bat: {frames_with_detections}")
print(f"Total detections: {total_detections}")
print(f"Detection rate: {frames_with_detections/total_frames*100:.1f}%")

# Get confidence stats
all_confidences = []
for r in results:
    if len(r.boxes) > 0:
        all_confidences.extend([float(box.conf) for box in r.boxes])

if all_confidences:
    print(f"\nConfidence scores:")
    print(f"  Min: {min(all_confidences):.3f}")
    print(f"  Max: {max(all_confidences):.3f}")
    print(f"  Avg: {sum(all_confidences)/len(all_confidences):.3f}")

print(f"\n✅ Results saved to: {OUTPUT_DIR / video_name}")
