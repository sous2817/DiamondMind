"""
Test YOLOv8 v3 Model on Real Video
Compare with v2.5 results
"""

from ultralytics import YOLO
import cv2
from pathlib import Path

# Configuration
MODEL_PATH = "yolo-bat-detection/models/v3_full_5329imgs/best.pt"
VIDEO_PATH = "C:/dm/docs/test-videos/bat3.mp4"
OUTPUT_PATH = "C:/dm/docs/test-videos/bat3_v3_output.mp4"
CONF_THRESHOLD = 0.25  # Standard confidence threshold

print("🏏 Testing YOLOv8 v3 Model")
print("=" * 50)
print(f"Model: {MODEL_PATH}")
print(f"Video: {VIDEO_PATH}")
print(f"Confidence: {CONF_THRESHOLD}")
print("=" * 50)

# Load model
model = YOLO(MODEL_PATH)

# Run inference
results = model.predict(
    source=VIDEO_PATH,
    conf=CONF_THRESHOLD,
    save=True,
    project="C:/dm/docs/test-videos",
    name="v3_predictions",
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

print("\n✅ Results saved to: C:/dm/docs/test-videos/v3_predictions")
