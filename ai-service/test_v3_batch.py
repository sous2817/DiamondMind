"""
Batch Test YOLOv8 v3 Model on Multiple Videos
Tests all videos in the test-videos directory and generates a summary report
"""

from ultralytics import YOLO
from pathlib import Path
import time

# Configuration
MODEL_PATH = "yolo-bat-detection/models/v3_full_5329imgs/best.pt"
VIDEO_DIR = Path("C:/dm/docs/test-videos")
OUTPUT_DIR = Path("C:/dm/docs/test-videos/v3_batch_results")
CONF_THRESHOLD = 0.25

print("🏏 YOLOv8 v3 Batch Video Testing")
print("=" * 70)
print(f"Model: {MODEL_PATH}")
print(f"Confidence Threshold: {CONF_THRESHOLD}")
print(f"Output Directory: {OUTPUT_DIR}")
print("=" * 70)

# Load model
print("\n📦 Loading model...")
model = YOLO(MODEL_PATH)
print("✅ Model loaded successfully")

# Find all MP4 videos
videos = list(VIDEO_DIR.glob("*.mp4"))
if not videos:
    print(f"❌ No MP4 videos found in {VIDEO_DIR}")
    exit(1)

print(f"\n📹 Found {len(videos)} videos to process")

# Results tracking
results_summary = []
total_start = time.time()

# Process each video
for idx, video_path in enumerate(videos, 1):
    video_name = video_path.stem
    
    print(f"\n{'='*70}")
    print(f"[{idx}/{len(videos)}] Processing: {video_name}.mp4")
    print('='*70)
    
    start_time = time.time()
    
    # Run inference
    results = model.predict(
        source=str(video_path),
        conf=CONF_THRESHOLD,
        save=True,
        project=str(OUTPUT_DIR),
        name=video_name,
        verbose=False  # Suppress per-frame output
    )
    
    elapsed = time.time() - start_time
    
    # Calculate statistics
    total_frames = len(results)
    frames_with_detections = sum(1 for r in results if len(r.boxes) > 0)
    total_detections = sum(len(r.boxes) for r in results)
    
    # Get confidence stats
    all_confidences = []
    for r in results:
        if len(r.boxes) > 0:
            all_confidences.extend([float(box.conf) for box in r.boxes])
    
    detection_rate = (frames_with_detections / total_frames * 100) if total_frames > 0 else 0
    
    # Print results
    print(f"  Total frames: {total_frames}")
    print(f"  Frames with bat: {frames_with_detections}")
    print(f"  Total detections: {total_detections}")
    print(f"  Detection rate: {detection_rate:.1f}%")
    
    if all_confidences:
        avg_conf = sum(all_confidences) / len(all_confidences)
        print(f"  Confidence: min={min(all_confidences):.3f}, max={max(all_confidences):.3f}, avg={avg_conf:.3f}")
    else:
        avg_conf = 0
        print(f"  Confidence: No detections")
    
    print(f"  Processing time: {elapsed:.1f}s")
    
    # Store summary
    results_summary.append({
        'video': video_name,
        'frames': total_frames,
        'detections': total_detections,
        'detection_rate': detection_rate,
        'avg_confidence': avg_conf if all_confidences else 0,
        'max_confidence': max(all_confidences) if all_confidences else 0,
        'time': elapsed
    })

total_elapsed = time.time() - total_start

# Print summary table
print("\n" + "=" * 70)
print("📊 BATCH PROCESSING SUMMARY")
print("=" * 70)
print(f"{'Video':<20} {'Frames':>8} {'Detections':>12} {'Rate':>8} {'Avg Conf':>10} {'Time':>8}")
print("-" * 70)

for result in results_summary:
    print(f"{result['video']:<20} {result['frames']:>8} {result['detections']:>12} "
          f"{result['detection_rate']:>7.1f}% {result['avg_confidence']:>10.3f} {result['time']:>7.1f}s")

print("-" * 70)
total_frames = sum(r['frames'] for r in results_summary)
total_detections = sum(r['detections'] for r in results_summary)
overall_rate = (total_detections / total_frames * 100) if total_frames > 0 else 0

print(f"{'TOTAL':<20} {total_frames:>8} {total_detections:>12} {overall_rate:>7.1f}% "
      f"{'':>10} {total_elapsed:>7.1f}s")

print("\n" + "=" * 70)
print(f"✅ All videos processed in {total_elapsed:.1f}s")
print(f"📁 Results saved to: {OUTPUT_DIR}")
print("=" * 70)

# Save summary to file
summary_file = OUTPUT_DIR / "batch_summary.txt"
summary_file.parent.mkdir(parents=True, exist_ok=True)

with open(summary_file, 'w') as f:
    f.write("YOLOv8 v3 Batch Testing Summary\n")
    f.write(f"Model: {MODEL_PATH}\n")
    f.write(f"Confidence Threshold: {CONF_THRESHOLD}\n")
    f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("\n" + "=" * 70 + "\n")
    f.write(f"{'Video':<20} {'Frames':>8} {'Detections':>12} {'Rate':>8} {'Avg Conf':>10} {'Time':>8}\n")
    f.write("-" * 70 + "\n")
    
    for result in results_summary:
        f.write(f"{result['video']:<20} {result['frames']:>8} {result['detections']:>12} "
                f"{result['detection_rate']:>7.1f}% {result['avg_confidence']:>10.3f} {result['time']:>7.1f}s\n")
    
    f.write("-" * 70 + "\n")
    f.write(f"{'TOTAL':<20} {total_frames:>8} {total_detections:>12} {overall_rate:>7.1f}% "
            f"{'':>10} {total_elapsed:>7.1f}s\n")

print(f"\n📄 Summary report saved to: {summary_file}")
