"""
YOLOv8 Bat Detection - Inference Script
DM-53: Create Annotated Dataset for YOLO Bat Detection Model

This script runs bat detection on new images or videos.

Usage:
    python inference.py --source video.mp4              # Detect in video
    python inference.py --source image.jpg              # Detect in image
    python inference.py --source folder/                # Detect in all images in folder
    python inference.py --source 0                      # Webcam (live detection)
"""

from ultralytics import YOLO
import argparse
import cv2
from pathlib import Path

def run_inference(
    model_path='models/v1_baseline_603imgs/best.pt',  # Updated path
    source='',
    conf_threshold=0.25,
    save_results=True,
    show_results=False
):
    """
    Run bat detection inference on images, videos, or webcam.
    
    Args:
        model_path: Path to trained model weights
        source: Path to image/video/folder or webcam ID (0)
        conf_threshold: Confidence threshold for detections (0-1)
        save_results: Save annotated images/videos
        show_results: Display results in window (not recommended for videos)
    """
    print("🏏 DiamondMind - Bat Detection Inference")
    print("=" * 50)
    
    # Check if model exists
    model_path = Path(model_path)
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        print("   Train a model first: python scripts/train.py")
        return
    
    print(f"📦 Loading model: {model_path}")
    model = YOLO(str(model_path))
    
    print(f"🎯 Running inference on: {source}")
    print(f"   Confidence threshold: {conf_threshold}")
    print("=" * 50)
    
    # Run inference
    results = model.predict(
        source=source,
        conf=conf_threshold,   # Confidence threshold
        iou=0.45,              # IoU threshold for NMS
        imgsz=640,             # Image size
        save=save_results,     # Save annotated predictions
        show=show_results,     # Show results in window
        verbose=True,          # Print results
        stream=True,           # Stream results (for videos)
        project='../../docs/test-videos',  # Output directory
        name='predictions',    # Subfolder name
        
        # Visualization settings
        show_labels=True,      # Show class labels
        show_conf=True,        # Show confidence scores
        line_width=2,          # Bounding box line width
    )
    
    # Process results
    total_detections = 0
    for idx, result in enumerate(results):
        # Get detection info
        boxes = result.boxes
        num_bats = len(boxes)
        total_detections += num_bats
        
        if num_bats > 0:
            print(f"\n📸 Frame/Image {idx + 1}: {num_bats} bat(s) detected")
            
            for i, box in enumerate(boxes):
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                print(f"   Bat {i + 1}:")
                print(f"      Confidence: {conf:.2%}")
                print(f"      Bounding Box: ({int(x1)}, {int(y1)}) to ({int(x2)}, {int(y2)})")
                print(f"      Size: {int(x2-x1)}x{int(y2-y1)} pixels")
        else:
            print(f"\n📸 Frame/Image {idx + 1}: No bats detected")
    
    print("\n" + "=" * 50)
    print(f"✅ Inference complete!")
    print(f"   Total detections: {total_detections}")
    
    if save_results:
        print(f"   📁 Results saved to: docs/test-videos/predictions/")
        print(f"   💡 Tip: Check annotated images/videos in that folder")


def real_time_detection(model_path='runs/detect/bat_detection/weights/best.pt'):
    """
    Run real-time bat detection from webcam.
    Press 'q' to quit.
    """
    print("📹 Starting real-time bat detection...")
    print("   Press 'q' to quit")
    
    # Check if model exists
    model_path = Path(model_path)
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return
    
    # Load model
    model = YOLO(str(model_path))
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        return
    
    print("✅ Webcam opened. Starting detection...")
    
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run inference
        results = model(frame, conf=0.25, verbose=False)
        
        # Draw results
        annotated_frame = results[0].plot()
        
        # Display
        cv2.imshow('DiamondMind - Bat Detection', annotated_frame)
        
        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Real-time detection stopped")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run YOLOv8 Bat Detection Inference')
    
    parser.add_argument('--model', type=str,
                        default='runs/detect/bat_detection/weights/best.pt',
                        help='Path to trained model weights')
    parser.add_argument('--source', type=str, required=True,
                        help='Source: image path, video path, folder, or webcam (0)')
    parser.add_argument('--conf', type=float, default=0.25,
                        help='Confidence threshold (0-1)')
    parser.add_argument('--no-save', action='store_true',
                        help='Do not save results')
    parser.add_argument('--show', action='store_true',
                        help='Display results in window')
    parser.add_argument('--webcam', action='store_true',
                        help='Run real-time webcam detection')
    
    args = parser.parse_args()
    
    if args.webcam:
        real_time_detection(args.model)
    else:
        run_inference(
            model_path=args.model,
            source=args.source,
            conf_threshold=args.conf,
            save_results=not args.no_save,
            show_results=args.show
        )
