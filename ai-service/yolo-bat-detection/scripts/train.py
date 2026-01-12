"""
YOLOv8 Bat Detection - Training Script
DM-53: Create Annotated Dataset for YOLO Bat Detection Model

This script trains a YOLOv8 model to detect baseball bats in swing videos.

Usage:
    python train.py                              # Default training
    python train.py --epochs 50 --imgsz 1280     # Custom config
    python train.py --model yolov8s.pt           # Use larger model
"""

from ultralytics import YOLO
import argparse
import os
from pathlib import Path

def train_bat_detector(
    model_size='yolov8n.pt',
    epochs=100,
    imgsz=640,
    batch=16,
    device='cpu',  # Change to 'cuda' or '0' if you have GPU
    project='runs/detect',
    name='bat_detection'
):
    """
    Train YOLOv8 model for bat detection.
    
    Args:
        model_size: Pre-trained model to start from (yolov8n.pt, yolov8s.pt, etc.)
        epochs: Number of training epochs
        imgsz: Input image size (640, 1280, etc.)
        batch: Batch size (reduce if OOM errors)
        device: 'cpu', 'cuda', or GPU ID ('0', '1', etc.)
        project: Root directory for saving runs
        name: Run name for this training session
    """
    
    # Verify dataset exists
    data_yaml = Path('dataset/data.yaml')
    if not data_yaml.exists():
        raise FileNotFoundError(
            f"Dataset configuration not found at {data_yaml}\n"
            "Please create dataset/data.yaml with your dataset paths."
        )
    
    print("🏏 DiamondMind - YOLOv8 Bat Detection Training")
    print("=" * 50)
    print(f"Model: {model_size}")
    print(f"Epochs: {epochs}")
    print(f"Image Size: {imgsz}")
    print(f"Batch Size: {batch}")
    print(f"Device: {device}")
    print("=" * 50)
    
    # Load pre-trained YOLO model
    model = YOLO(model_size)
    
    # Train the model
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=project,
        name=name,
        
        # Hyperparameters (optimized for bat detection)
        lr0=0.01,              # Initial learning rate
        lrf=0.01,              # Final learning rate (as fraction of lr0)
        momentum=0.937,        # SGD momentum
        weight_decay=0.0005,   # L2 regularization
        warmup_epochs=3.0,     # Warmup epochs
        warmup_momentum=0.8,   # Warmup initial momentum
        
        # Data augmentation (critical for small datasets)
        hsv_h=0.015,           # HSV-Hue augmentation
        hsv_s=0.7,             # HSV-Saturation
        hsv_v=0.4,             # HSV-Value
        degrees=0.0,           # Rotation (0 for bats - they're always oriented similarly)
        translate=0.1,         # Translation
        scale=0.5,             # Scaling
        shear=0.0,             # Shear (0 for bats)
        perspective=0.0,       # Perspective (0 for bats)
        flipud=0.0,            # Vertical flip (0 - bats don't flip vertically)
        fliplr=0.5,            # Horizontal flip (50% - left/right handed batters)
        mosaic=1.0,            # Mosaic augmentation (4 images combined)
        mixup=0.15,            # Mixup augmentation (blend images)
        
        # Training settings
        patience=50,           # Early stopping patience (epochs)
        save=True,             # Save checkpoints
        save_period=-1,        # Save every N epochs (-1 = only save last/best)
        cache=False,           # Cache images (True if you have RAM)
        workers=8,             # Number of worker threads
        
        # Validation
        val=True,              # Validate during training
        plots=True,            # Generate plots (confusion matrix, etc.)
        
        # Advanced
        amp=True,              # Automatic Mixed Precision (faster on GPU)
        pretrained=True,       # Use pre-trained weights
        verbose=True,          # Verbose output
    )
    
    print("\n✅ Training Complete!")
    print(f"📊 Results saved to: {results.save_dir}")
    print(f"🏆 Best model: {results.save_dir}/weights/best.pt")
    print(f"📈 Metrics: {results.save_dir}/results.png")
    
    # Print final metrics
    if hasattr(results, 'results_dict'):
        metrics = results.results_dict
        print("\n📊 Final Metrics:")
        print(f"   mAP@50: {metrics.get('metrics/mAP50(B)', 'N/A'):.3f}")
        print(f"   Precision: {metrics.get('metrics/precision(B)', 'N/A'):.3f}")
        print(f"   Recall: {metrics.get('metrics/recall(B)', 'N/A'):.3f}")
    
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train YOLOv8 Bat Detection Model')
    
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                        help='Model size: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs')
    parser.add_argument('--imgsz', type=int, default=640,
                        help='Input image size (640, 1280, etc.)')
    parser.add_argument('--batch', type=int, default=16,
                        help='Batch size (reduce if OOM)')
    parser.add_argument('--device', type=str, default='cpu',
                        help='Device: cpu, cuda, 0, 1, etc.')
    parser.add_argument('--name', type=str, default='bat_detection',
                        help='Run name for this training session')
    
    args = parser.parse_args()
    
    # Train the model
    train_bat_detector(
        model_size=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        name=args.name
    )
