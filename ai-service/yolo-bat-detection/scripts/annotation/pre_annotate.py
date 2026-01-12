"""
Pre-Annotation Script for Label Studio
Uses trained YOLOv8 model to generate initial annotations for new images

This script:
1. Runs YOLOv8 inference on a folder of images
2. Generates Label Studio JSON format annotations
3. Also creates YOLO format labels for direct use

Usage:
    python pre_annotate.py --images path/to/images/ --output annotations.json
"""

from ultralytics import YOLO
from pathlib import Path
import json
import argparse
from PIL import Image

def yolo_to_label_studio(image_path, detections, image_id):
    """
    Convert YOLO detections to Label Studio format.
    
    Args:
        image_path: Path to the image
        detections: YOLO detection results
        image_id: Unique ID for this image
    
    Returns:
        Label Studio task dict
    """
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    # Label Studio annotations
    annotations = []
    
    for det in detections.boxes:
        # Get bounding box coordinates (normalized 0-1)
        x1, y1, x2, y2 = det.xyxyn[0].cpu().numpy()
        conf = float(det.conf[0])
        
        # Convert to Label Studio format (percentage 0-100)
        # Label Studio uses: x (left), y (top), width, height as percentages
        x_percent = float(x1 * 100)
        y_percent = float(y1 * 100)
        width_percent = float((x2 - x1) * 100)
        height_percent = float((y2 - y1) * 100)
        
        annotation = {
            "value": {
                "x": x_percent,
                "y": y_percent,
                "width": width_percent,
                "height": height_percent,
                "rectanglelabels": ["bat"]
            },
            "from_name": "label",
            "to_name": "image",
            "type": "rectanglelabels",
            "score": conf  # Confidence score for review
        }
        
        annotations.append(annotation)
    
    # Label Studio task format
    task = {
        "data": {
            "image": f"/data/local-files/?d={image_path.name}"  # Local file path
        },
        "predictions": [{
            "model_version": "yolov8n_v1_baseline",
            "score": float(sum(a["score"] for a in annotations) / len(annotations)) if annotations else 0,
            "result": annotations
        }] if annotations else []
    }
    
    return task


def yolo_to_yolo_labels(detections):
    """
    Convert YOLO detections to YOLO label format.
    
    Returns:
        List of label lines in YOLO format
    """
    labels = []
    
    for det in detections.boxes:
        # Get normalized coordinates
        x1, y1, x2, y2 = det.xyxyn[0].cpu().numpy()
        
        # Convert to YOLO format (center_x, center_y, width, height)
        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2
        width = x2 - x1
        height = y2 - y1
        
        # YOLO format: class_id x_center y_center width height
        label = f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
        labels.append(label)
    
    return labels


def pre_annotate(
    images_dir,
    model_path='models/v1_baseline_603imgs/best.pt',
    output_json='pre_annotations.json',
    output_labels_dir=None,
    conf_threshold=0.25
):
    """
    Pre-annotate images using trained YOLO model.
    
    Args:
        images_dir: Directory containing images to annotate
        model_path: Path to trained model
        output_json: Output file for Label Studio format
        output_labels_dir: Optional directory to save YOLO format labels
        conf_threshold: Confidence threshold for detections
    """
    print("🤖 YOLOv8 Pre-Annotation for Label Studio")
    print("=" * 50)
    
    # Load model
    print(f"📦 Loading model: {model_path}")
    model = YOLO(model_path)
    
    # Find images
    images_dir = Path(images_dir)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = [f for f in images_dir.glob('*') if f.suffix.lower() in image_extensions]
    
    print(f"📸 Found {len(image_files)} images")
    
    if not image_files:
        print("❌ No images found!")
        return
    
    # Create output directory for YOLO labels if specified
    if output_labels_dir:
        output_labels_dir = Path(output_labels_dir)
        output_labels_dir.mkdir(parents=True, exist_ok=True)
    
    # Process images
    tasks = []
    total_detections = 0
    
    for idx, image_file in enumerate(image_files, 1):
        print(f"\n[{idx}/{len(image_files)}] Processing: {image_file.name}")
        
        # Run inference
        results = model(str(image_file), conf=conf_threshold, verbose=False)[0]
        
        num_detections = len(results.boxes)
        total_detections += num_detections
        print(f"   Found {num_detections} bat(s)")
        
        # Convert to Label Studio format
        task = yolo_to_label_studio(image_file, results, idx)
        tasks.append(task)
        
        # Optionally save YOLO format labels
        if output_labels_dir:
            label_file = output_labels_dir / f"{image_file.stem}.txt"
            labels = yolo_to_yolo_labels(results)
            
            if labels:
                with open(label_file, 'w') as f:
                    f.write('\n'.join(labels))
    
    # Save Label Studio JSON
    print("\n" + "=" * 50)
    print(f"💾 Saving annotations to: {output_json}")
    
    with open(output_json, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    print(f"✅ Pre-annotation complete!")
    print(f"   Total images: {len(image_files)}")
    print(f"   Total detections: {total_detections}")
    print(f"   Average: {total_detections / len(image_files):.1f} bats per image")
    
    if output_labels_dir:
        print(f"   YOLO labels saved to: {output_labels_dir}")
    
    print("\n📝 Next Steps:")
    print("   1. Install Label Studio: pip install label-studio")
    print("   2. Start Label Studio: label-studio start")
    print("   3. Create a new project")
    print("   4. Import this JSON file")
    print("   5. Review and correct the pre-annotations!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-annotate images for Label Studio')
    
    parser.add_argument('--images', type=str, required=True,
                        help='Directory containing images to annotate')
    parser.add_argument('--model', type=str,
                        default='models/v1_baseline_603imgs/best.pt',
                        help='Path to trained YOLOv8 model')
    parser.add_argument('--output', type=str,
                        default='pre_annotations.json',
                        help='Output JSON file for Label Studio')
    parser.add_argument('--labels', type=str,
                        help='Optional: directory to save YOLO format labels')
    parser.add_argument('--conf', type=float, default=0.25,
                        help='Confidence threshold (0-1)')
    
    args = parser.parse_args()
    
    pre_annotate(
        images_dir=args.images,
        model_path=args.model,
        output_json=args.output,
        output_labels_dir=args.labels,
        conf_threshold=args.conf
    )
