# YOLOv8 v3 Model - Full Dataset

## Overview
Production-ready YOLOv8n model trained on full annotated dataset with proper validation metrics.

## Training Details
- **Model**: YOLOv8n (nano)
- **Dataset**: 5,329 images total
  - Train: 3,650 images
  - Validation: 839 images  
  - Test: 840 images
- **Training Date**: January 21, 2026
- **Epochs**: 100 (with early stopping patience: 50)
- **Batch Size**: 16 (GPU memory optimized)
- **Image Size**: 640x640
- **Device**: NVIDIA GPU
- **Training Time**: ~3-4 hours

## Performance Metrics

### Validation Metrics (Final)
- **mAP@50**: 73.4% ✅
- **mAP@50-95**: 45.1%
- **Precision**: 80.7%
- **Recall**: 67.0%

### Test Video Results (bat3.mp4)
- **Total Frames**: 202
- **Detections**: 25 frames (12.4% detection rate)
- **Confidence Range**: 0.263 - 0.783
- **Average Confidence**: 0.506

### Comparison to Previous Models
| Model | Dataset Size | mAP@50 | Precision | Recall |
|-------|-------------|--------|-----------|--------|
| v1    | 603 imgs    | 44.4%  | 58.8%     | 46.2%  |
| v2    | 725 imgs    | 38.0%  | 64.6%     | 35.5%  |
| v2.5  | 2,000 imgs  | N/A*   | N/A       | N/A    |
| **v3**| **5,329 imgs** | **73.4%** | **80.7%** | **67.0%** |

*v2.5 had no labeled validation set

## Model Files
- **Weights**: `best.pt` (6.2 MB)
- **Results**: `results.png`
- **Metrics**:
  - Confusion Matrix: `confusion_matrix.png`
  - Precision-Recall Curve: `BoxPR_curve.png`
  - F1 Curve: `BoxF1_curve.png`
  - Precision Curve: `BoxP_curve.png`
  - Recall Curve: `BoxR_curve.png`

## Training Configuration
```yaml
# Optimized hyperparameters
lr0: 0.01              # Initial learning rate
lrf: 0.01              # Final learning rate
momentum: 0.937        # SGD momentum
weight_decay: 0.0005   # L2 regularization
warmup_epochs: 3.0     # Warmup epochs

# Data augmentation (reduced for speed)
hsv_h: 0.015
hsv_s: 0.5
hsv_v: 0.3
degrees: 0.0           # No rotation (bats oriented similarly)
fliplr: 0.5            # Horizontal flip for left/right batters
mosaic: 0.8

# Performance settings
cache: 'disk'          # Disk caching (RAM too large for 5.3k images)
workers: 4             # Parallel workers
amp: True              # Mixed precision training
```

## Usage

### Inference on Video
```python
from ultralytics import YOLO

model = YOLO('models/v3_full_5329imgs/best.pt')
results = model.predict(
    source='video.mp4',
    conf=0.25,  # Confidence threshold
    save=True
)
```

### Inference on Images
```python
results = model.predict(
    source='images/',
    conf=0.25,
    save_txt=True  # Save YOLO format labels
)
```

## Next Steps
1. **Export to ONNX** for faster inference
2. **Integrate into ai-service** (DM-66: Replace HSV tracking)
3. **Deploy to production**

## Notes
- Production-ready for DiamondMind bat tracking
- Significantly outperforms color-based HSV detection
- High precision (80.7%) means fewer false positives
- Solid recall (67.0%) captures most bat instances across video frames
- Ready to replace current bat detection system
