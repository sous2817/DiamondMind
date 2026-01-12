# Model: YOLOv8n Bat Detection v1 (Baseline)

## Training Info
- **Date**: 2026-01-12
- **Training Time**: 10 minutes (GPU)
- **Hardware**: NVIDIA GTX 1660 SUPER (6GB)
- **Framework**: Ultralytics YOLOv8.3.252 + PyTorch 2.5.1+cu121

## Dataset
- **Total Images**: 749 (603 train / 96 valid / 50 test)
- **Source**: Roboflow YOLOv8 format (converted from polygon)
- **Classes**: 1 (bat)
- **Annotations**: Bounding boxes

## Training Configuration
- **Model**: YOLOv8n (3M parameters, 8.2 GFLOPs)
- **Epochs**: 50
- **Batch Size**: 16
- **Image Size**: 640x640
- **Device**: cuda:0

## Performance Metrics
- **mAP@50**: 44.4%
- **mAP@50-95**: 27.9%
- **Precision**: 58.8%
- **Recall**: 46.2%
- **Inference Speed**: 14.2ms per frame (GPU)

## Model Characteristics
- **Conservative detection**: Low false positive rate (59% precision)
- **Moderate recall**: Misses some visible bats (46% recall)
- **Fast inference**: Suitable for real-time processing

## Use Cases
- Baseline for comparison
- Proof-of-concept for YOLO-based bat detection
- Replacement for HSV color-based tracking

## Known Limitations
- 44% mAP below production target (85%+)
- Trained on limited dataset (603 images)
- May struggle with:
  - Wood bats vs metal bats
  - Heavy motion blur
  - Unusual batting stances
  
## Improvement Recommendations
1. Collect 2000+ annotated images
2. Include more diverse:
   - Bat types (wood, metal, colors)
   - Lighting conditions
   - Camera angles
3. Train for 100+ epochs
4. Consider YOLOv8m (medium) for better accuracy

## Files
- `best.pt` - Best model weights (6.2 MB)
- Training artifacts in: `training_runs/2026-01-12_gpu_50epochs/`

## Version History
- **v1**: Initial baseline model (2026-01-12)
