"""
YOLOv8 Bat Detection - Validation Script
DM-53: Create Annotated Dataset for YOLO Bat Detection Model

This script validates a trained YOLOv8 model and checks annotation quality.

Usage:
    python validate_dataset.py                              # Validate C:/Annotations
    python validate_dataset.py --dataset-root path/to/data  # Custom dataset
    python validate_dataset.py --data path/to/data.yaml     # With data.yaml
"""

from ultralytics import YOLO
import argparse
import yaml
from pathlib import Path
import os

def validate_dataset_format(dataset_root='C:/Annotations', data_yaml_path=None):
    """
    Validate YOLO dataset format and check for common issues.
    
    Args:
        dataset_root: Root directory containing train/valid/test folders
        data_yaml_path: Optional path to data.yaml (will be skipped if not provided)
    
    Returns:
        bool: True if dataset is valid, False otherwise
    """
    print("🔍 Validating Dataset Format...")
    print("=" * 50)
    
    dataset_root = Path(dataset_root)
    
    # Check if dataset root exists
    if not dataset_root.exists():
        print(f"❌ Dataset root not found: {dataset_root}")
        return False
    
    print(f"📁 Dataset root: {dataset_root}")
    
    # If data.yaml provided, validate it
    if data_yaml_path:
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
    else:
        print("⚠️  No data.yaml provided, skipping config validation")
    
    # Check each split
    all_valid = True
    for split in ['train', 'valid', 'test']:
        split_dir = dataset_root / split
        
        if not split_dir.exists():
            print(f"\n⚠️  {split.upper()} split directory not found: {split_dir}")
            continue
            
        img_dir = split_dir / 'images'
        lbl_dir = split_dir / 'labels'
        
        if not img_dir.exists():
            print(f"❌ {split}/images directory not found")
            all_valid = False
            continue
        
        # Labels directory is optional (might not have labels yet)
        if not lbl_dir.exists():
            print(f"⚠️  {split}/labels directory not found (creating it)")
            lbl_dir.mkdir(parents=True, exist_ok=True)
        
        # Count images and labels
        images = list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.png'))
        labels = list(lbl_dir.glob('*.txt'))
        
        print(f"\n📂 {split.upper()} Split:")
        print(f"   Images: {len(images)}")
        print(f"   Labels: {len(labels)}")
        
        if len(images) == 0:
            print(f"   ⚠️  No images found in {split}/images")
            continue
        
        # Check for mismatches
        missing_labels = []
        for img in images:
            label_path = lbl_dir / f"{img.stem}.txt"
            if not label_path.exists():
                missing_labels.append(img.name)
        
        if missing_labels:
            print(f"   ⚠️  {len(missing_labels)} images missing labels ({len(missing_labels)/len(images)*100:.1f}%)")
            if len(labels) == 0:
                print(f"      This is expected if you haven't annotated this split yet")
            else:
                print(f"      First 5 missing:")
                for lbl in missing_labels[:5]:
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
                    all_valid = False
                    continue
                
                # Check if values are normalized [0, 1]
                try:
                    class_id, x, y, w, h = map(float, parts)
                    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                        print(f"   ❌ Coordinates not normalized in {sample_label.name}")
                        print(f"      x={x}, y={y}, w={w}, h={h}")
                        all_valid = False
                        continue
                    
                    if class_id != 0:  # Should be 0 for 'bat' class
                        print(f"   ⚠️  Unexpected class ID: {class_id} (expected 0)")
                    
                except ValueError:
                    print(f"   ❌ Non-numeric values in {sample_label.name}")
                    all_valid = False
                    continue
        
            print(f"   ✅ {split} split format valid")
        else:
            print(f"   ⚠️  No labels to validate")
    
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ Dataset validation passed!")
    else:
        print("⚠️  Dataset has some issues (see above)")
    return all_valid


def validate_model(model_path='runs/detect/bat_detection/weights/best.pt', 
                   data_yaml='C:/Annotations/data.yaml'):
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
        print("   Have you trained a model yet? Run: python scripts/training/train.py")
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
    
    parser.add_argument('--dataset-root', type=str, 
                        default='C:/Annotations',
                        help='Root directory containing train/valid/test folders')
    parser.add_argument('--model', type=str, 
                        default='runs/detect/bat_detection/weights/best.pt',
                        help='Path to trained model weights')
    parser.add_argument('--data', type=str, default=None,
                        help='Path to dataset configuration (optional)')
    parser.add_argument('--check-dataset', action='store_true',
                        help='Only validate dataset format (skip model validation)')
    
    args = parser.parse_args()
    
    # Always check dataset format
    dataset_valid = validate_dataset_format(args.dataset_root, args.data)
    
    # Only validate model if requested and dataset is valid
    if not args.check_dataset and dataset_valid:
        if args.data:
            validate_model(args.model, args.data)
        else:
            print("\n⚠️  No data.yaml provided, skipping model validation")
    elif not dataset_valid:
        print("\n❌ Fix dataset issues before training/validating model")
