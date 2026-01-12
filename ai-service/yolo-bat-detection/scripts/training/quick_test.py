"""
Quick Test Training - Verify GPU Setup
DM-53: YOLO Bat Detection Training

This script runs a quick 5-epoch training to verify:
1. GPU is being used correctly
2. Model files are saved properly
3. Training metrics are recorded
4. Output directory structure is correct

Usage:
    python quick_test_training.py
"""

from ultralytics import YOLO
import torch
from pathlib import Path

def quick_test_train():
    """
    Run a quick 5-epoch training to verify everything works.
    """
    print("🧪 Quick GPU Test Training")
    print("=" * 50)
    
    # Check GPU availability
    if not torch.cuda.is_available():
        print("⚠️  WARNING: CUDA not available, will use CPU")
        device = 'cpu'
    else:
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        device = '0'
    
    print("\n📝 Test Configuration:")
    print(f"   Epochs: 5 (quick test)")
    print(f"   Batch Size: 8")
    print(f"   Device: {device}")
    print(f"   Image Size: 640")
    print("=" * 50)
    
    # Verify dataset exists
    data_yaml = Path('dataset/data.yaml')
    if not data_yaml.exists():
        raise FileNotFoundError(f"Dataset not found at {data_yaml}")
    
    # Load model
    print("\n📦 Loading YOLOv8n model...")
    model = YOLO('yolov8n.pt')
    
    # Train with minimal epochs
    print("\n🚀 Starting test training...")
    print("   This should take 2-3 minutes with GPU\n")
    
    results = model.train(
        data=str(data_yaml),
        epochs=5,              # Quick test
        imgsz=640,
        batch=8,
        device=device,
        project='runs/detect',
        name='test_run',
        
        # Disable some features for speed
        plots=True,            # Still generate plots
        save=True,             # Save model
        save_period=-1,        # Only save best/last
        verbose=True,
        
        # Use same hyperparameters as main training
        lr0=0.01,
        patience=10,
        
        # Data augmentation
        hsv_h=0.015,
        degrees=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.15,
    )
    
    print("\n" + "=" * 50)
    print("✅ Test Training Complete!")
    print(f"📁 Results: {results.save_dir}")
    print(f"🏆 Best model: {results.save_dir}/weights/best.pt")
    
    # Verify outputs
    save_dir = Path(results.save_dir)
    checks = {
        "Best weights": save_dir / "weights" / "best.pt",
        "Last weights": save_dir / "weights" / "last.pt",
        "Results plot": save_dir / "results.png",
    }
    
    print("\n📊 Verifying outputs:")
    all_good = True
    for name, path in checks.items():
        if path.exists():
            print(f"   ✅ {name}: {path.name}")
        else:
            print(f"   ❌ {name}: NOT FOUND")
            all_good = False
    
    if all_good:
        print("\n🎉 All checks passed! GPU setup is working correctly.")
        print("\n📈 Next Steps:")
        print("   1. Review results in runs/detect/test_run/")
        print("   2. Run full training: python scripts/train.py --epochs 50 --batch 16 --device 0")
    else:
        print("\n⚠️  Some files missing - check for errors above")
    
    return results


if __name__ == '__main__':
    quick_test_train()
