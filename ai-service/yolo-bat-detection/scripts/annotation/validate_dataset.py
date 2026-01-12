"""
YOLOv8 Bat Detection - Validation Script
DM-53: Create Annotated Dataset for YOLO Bat Detection Model

This script validates a trained YOLOv8 model and checks annotation quality.

Usage:
    python validate.py                           # Use best.pt from latest run
    python validate.py --model path/to/best.pt   # Custom model
    python validate.py --check-dataset           # Only validate dataset format
"""

from ultralytics import YOLO
import argparse
import yaml
from pathlib import Path
import os

def validate_dataset_format(data_yaml_path='dataset/data.yaml'):
    """
    Validate YOLO dataset format and check for common issues.
    
    Returns:
        bool: True if dataset is valid, False otherwise
    """
    print("🔍 Validating Dataset Format...")
    print("=" * 50)
    
    # Check data.yaml exists
    data_yaml = Path(data_yaml_path)
    if not data_yaml.exists():
        print(f"❌ data.yaml not found at {data_yaml}")
        return False
    
    # Load configuration
    with open(data_yaml, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check required fields
    required_fields = ['train', 'val', 'nc', 'names']
    for field in required_fields:
        if field not in config:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Verify class count matches names
    if config['nc'] != len(config['names']):
        print(f"❌ Class count mismatch: nc={config['nc']}, but {len(config['names'])} names provided")
        return False
    
    print(f"✅ Config valid - {config['nc']} class(es): {config['names']}")
    
    # Check each split
    for split in ['train', 'valid', 'test']:
        if split not in config:
            continue
            
        img_dir = Path('dataset') / split / 'images'
        lbl_dir = Path('dataset') / split / 'labels'
        
        if not img_dir.exists():
            print(f"❌ {split}/images directory not found")
            return False
        
        if not lbl_dir.exists():
            print(f"❌ {split}/labels directory not found")
            return False
        
        # Count images and labels
        images = list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.png'))
        labels = list(lbl_dir.glob('*.txt'))
        
        print(f"\n📂 {split.upper()} Split:")
        print(f"   Images: {len(images)}")
        print(f"   Labels: {len(labels)}")
        
        # Check for mismatches
        missing_labels = []
        for img in images:
            label_path = lbl_dir / f"{img.stem}.txt"
            if not label_path.exists():
                missing_labels.append(img.name)
        
        if missing_labels:
            print(f"   ⚠️  {len(missing_labels)} images missing labels:")
            for lbl in missing_labels[:5]:  # Show first 5
                print(f"      - {lbl}")
            if len(missing_labels) > 5:
                print(f"      ... and {len(missing_labels) - 5} more")
        
        # Validate label format (sample check)
        if labels:
            sample_label = labels[0]
            with open(sample_label, 'r') as f:
                lines = f.readlines()
            
            if lines:
                parts = lines[0].strip().split()
                if len(parts) != 5:
                    print(f"   ❌ Invalid label format in {sample_label.name}")
                    print(f"      Expected: class x y w h")
                    print(f"      Got: {parts}")
                    return False
                
                # Check if values are normalized [0, 1]
                try:
                    class_id, x, y, w, h = map(float, parts)
                    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                        print(f"   ❌ Coordinates not normalized in {sample_label.name}")
                        print(f"      x={x}, y={y}, w={w}, h={h}")
                        return False
                    
                    if class_id != 0:  # Should be 0 for 'bat' class
                        print(f"   ⚠️  Unexpected class ID: {class_id} (expected 0)")
                    
                except ValueError:
                    print(f"   ❌ Non-numeric values in {sample_label.name}")
                    return False
        
        print(f"   ✅ {split} split format valid")
    
    print("\n" + "=" * 50)
    print("✅ Dataset validation passed!")
    return True


def validate_model(model_path='runs/detect/bat_detection/weights/best.pt', 
                   data_yaml='dataset/data.yaml'):
    """
    Validate a trained YOLOv8 model on the validation set.
    
    Args:
        model_path: Path to trained model weights
        data_yaml: Path to dataset configuration
    """
    print("\n🎯 Validating Model Performance...")
    print("=" * 50)
    
    # Check if model exists
    model_path = Path(model_path)
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        print("   Have you trained a model yet? Run: python scripts/train.py")
        return
    
    # Load model
    model = YOLO(str(model_path))
    
    # Validate on test/validation set
    results = model.val(
        data=data_yaml,
        split='val',       # Use validation split
        batch=16,
        imgsz=640,
        plots=True,        # Generate confusion matrix, etc.
        save_json=True,    # Save results as JSON
        verbose=True
    )
    
    # Print metrics
    print("\n📊 Validation Metrics:")
    print("=" * 50)
    print(f"mAP@50:     {results.box.map50:.3f}   {'✅' if results.box.map50 > 0.80 else '⚠️'}")
    print(f"mAP@50-95:  {results.box.map:.3f}    {'✅' if results.box.map > 0.60 else '⚠️'}")
    print(f"Precision:  {results.box.mp:.3f}     {'✅' if results.box.mp > 0.75 else '⚠️'}")
    print(f"Recall:     {results.box.mr:.3f}     {'✅' if results.box.mr > 0.70 else '⚠️'}")
    
    print("\n📈 Interpretation:")
    if results.box.map50 > 0.85:
        print("✅ Excellent performance! Model is production-ready.")
    elif results.box.map50 > 0.70:
        print("✅ Good performance. Consider more training or data.")
    elif results.box.map50 > 0.50:
        print("⚠️  Moderate performance. Needs improvement.")
        print("   Suggestions:")
        print("   - Add more diverse training images")
        print("   - Train for more epochs")
        print("   - Check annotation quality")
    else:
        print("❌ Poor performance. Immediate action needed.")
        print("   Suggestions:")
        print("   - Review annotation quality carefully")
        print("   - Ensure dataset has diversity (bat types, lighting)")
        print("   - Train for 150-200 epochs")
        print("   - Consider data augmentation")
    
    print(f"\n📁 Results saved to: {results.save_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate YOLOv8 Bat Detection Model')
    
    parser.add_argument('--model', type=str, 
                        default='runs/detect/bat_detection/weights/best.pt',
                        help='Path to trained model weights')
    parser.add_argument('--data', type=str, default='dataset/data.yaml',
                        help='Path to dataset configuration')
    parser.add_argument('--check-dataset', action='store_true',
                        help='Only validate dataset format (skip model validation)')
    
    args = parser.parse_args()
    
    # Always check dataset format
    dataset_valid = validate_dataset_format(args.data)
    
    # Only validate model if requested and dataset is valid
    if not args.check_dataset and dataset_valid:
        validate_model(args.model, args.data)
    elif not dataset_valid:
        print("\n❌ Fix dataset issues before training/validating model")
