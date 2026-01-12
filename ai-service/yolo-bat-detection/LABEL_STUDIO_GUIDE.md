# Label Studio Pre-Annotation Workflow

This guide shows how to use your trained v1 model to pre-annotate new images, saving hours of manual work!

## Quick Start

### 1. Install Label Studio
```powershell
pip install label-studio
```

### 2. Pre-Annotate New Images
```powershell
cd c:\dm\ai-service\yolo-bat-detection

# Generate Label Studio annotations
python pre_annotate.py --images "path\to\new\images" --output "new_batch.json"

# Optional: Also save YOLO labels
python pre_annotate.py --images "path\to\new\images" --output "new_batch.json" --labels "dataset\train\labels"
```

### 3. Start Label Studio
```powershell
label-studio start
```
Opens at: http://localhost:8080

### 4. Import Pre-Annotations

1. Create new project in Label Studio
2. **Labeling Setup** → Use this XML template:
```xml
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="bat" background="green"/>
  </RectangleLabels>
</View>
```
3. **Import** → Upload `new_batch.json`
4. Review & correct the pre-annotations!

## Benefits

✅ **Faster annotation:** Just verify/correct instead of drawing from scratch  
✅ **Consistent quality:** Model provides baseline annotations  
✅ **Batch processing:** Annotate hundreds of images quickly  
✅ **YOLO export:** Export directly to YOLO format when done

## Workflow Tips

### Confidence Thresholds
- `--conf 0.25` (default): More detections, more false positives to correct
- `--conf 0.5`: Fewer detections, more missed bats to add
- **Recommended:** Start with 0.25, you can delete false positives faster than adding missed ones

### Review Strategy
1. **Quick pass:** Delete obvious false positives
2. **Detail pass:** Add missed bats and adjust box sizes
3. **Final pass:** Ensure all bats are tightly boxed

### Export from Label Studio
1. **Export** → **YOLO** format
2. Download annotations
3. Place in `dataset/train/labels/`

## Advanced: Active Learning Loop

```powershell
# 1. Pre-annotate batch 1
python pre_annotate.py --images batch1/ --output batch1.json

# 2. Review in Label Studio → export to dataset/

# 3. Train v2 model
python scripts\train.py --epochs 50 --batch 16 --device 0

# 4. Use v2 to pre-annotate batch 2 (better accuracy!)
python pre_annotate.py --model models/v2/best.pt --images batch2/ --output batch2.json

# 5. Repeat!
```

Each iteration improves the model, making pre-annotations more accurate!

## Troubleshooting

**"No detections found"**
- Lower confidence: `--conf 0.15`
- Check if images contain bats at similar angles to training data

**"Too many false positives"**
- Raise confidence: `--conf 0.4`
- Still faster to delete than annotate from scratch

**"Label Studio won't import"**
- Check JSON format: `python -m json.tool new_batch.json`
- Verify image paths are accessible

## Example: Annotating 1000 New Images

**Without pre-annotation:**
- 1000 images × 30 seconds each = **8.3 hours**

**With pre-annotation:**
- Pre-annotate: 1000 images × 0.1 seconds = 2 minutes
- Review/correct: 1000 images × 10 seconds each = **2.8 hours**

**Time saved: 5.5 hours!** ⚡
