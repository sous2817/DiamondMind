# YOLOv8 Bat Detection - Project Structure

## Directory Organization

```
yolo-bat-detection/
├── scripts/
│   ├── training/          # Model training scripts
│   ├── inference/         # Prediction and export
│   ├── annotation/        # Annotation workflow tools
│   └── utils/             # Data conversion utilities
│
├── models/                # Trained model versions
├── dataset/               # Training data
├── training_runs/         # Training outputs (gitignored)
├── tools/                 # Setup and configuration scripts
└── docs/                  # Documentation
```

## Quick Start Commands

### Training
```powershell
# Full training (50 epochs)
python scripts/training/train.py --epochs 50 --batch 16 --device 0

# Quick test (5 epochs)
python scripts/training/quick_test.py
```

### Annotation Workflow
```powershell
# 1. Split new images into train/valid/test
python scripts/annotation/split_dataset.py --source "C:\path\to\images"

# 2. Pre-annotate with trained model
python scripts/annotation/pre_annotate.py --images "path/to/images" --output "annotations.json"

# 3. Validate dataset format
python scripts/annotation/validate_dataset.py
```

### Inference
```powershell
# Predict on video
python scripts/inference/predict.py --source "video.mp4"

# Export model to ONNX
python scripts/inference/export.py --format onnx
```

### Utilities
```powershell
# Convert polygon annotations to bounding boxes
python scripts/utils/convert_polygon_to_bbox.py

# Setup GPU training
.\tools\setup_gpu_training.ps1
```

## Documentation

- **[README.md](docs/README.md)** - Full project documentation
- **[LABEL_STUDIO_GUIDE.md](docs/LABEL_STUDIO_GUIDE.md)** - Label Studio workflow guide

## Model Versions

- **v1_baseline_603imgs/** - Original Roboflow data (44.4% mAP)
- **v2_realworld_725imgs/** - Production model (64.6% precision)

## Next Steps

1. Annotate more real-world images (target: 2000+)
2. Train v3 with larger dataset
3. Integrate into AI service (DM-54)
