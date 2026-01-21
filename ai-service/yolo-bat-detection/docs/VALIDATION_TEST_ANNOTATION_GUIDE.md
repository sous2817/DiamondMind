# Validation & Test Set Annotation Guide

## Overview
You have **3,650 training images** annotated ✅  
Now annotating: **839 validation + 840 test = 1,679 images**

## Directory Structure (Confirmed)
```
C:\Annotations\
├── train/
│   ├── images/          (3,917 images)
│   └── labels/          (3,650 annotations)
├── valid/
│   ├── images/          (839 images) ← Annotate these
│   └── labels/          (empty for now)
└── test/
    ├── images/          (840 images) ← Annotate these
    └── labels/          (empty for now)
```

## Step-by-Step Process

### 1. Generate Pre-Annotations for Validation Set

```powershell
cd C:\dm\ai-service\venv\Scripts
.\python.exe ..\..\yolo-bat-detection\scripts\annotation\pre_annotate.py `
  --model ../../yolo-bat-detection/models/v2.5_realworld_2000imgs/best.pt `
  --images C:\Annotations\valid\images `
  --output C:\Annotations\valid_annotations_v2.5.json `
  --dataset-root C:\Annotations `
  --conf 0.15
```

**Expected output:** `valid_annotations_v2.5.json` (~839 tasks)

### 2. Fix JSON Paths for Validation

```powershell
.\python.exe ..\..\yolo-bat-detection\fix_label_studio_paths.py `
  C:\Annotations\valid_annotations_v2.5.json `
  C:\Annotations\valid_annotations_v2.5_fixed.json `
  valid/images
```

**Critical:** Use `valid/images` prefix (not just `valid`)

### 3. Generate Pre-Annotations for Test Set

```powershell
.\python.exe ..\..\yolo-bat-detection\scripts\annotation\pre_annotate.py `
  --model ../../yolo-bat-detection/models/v2.5_realworld_2000imgs/best.pt `
  --images C:\Annotations\test\images `
  --output C:\Annotations\test_annotations_v2.5.json `
  --dataset-root C:\Annotations `
  --conf 0.15
```

**Expected output:** `test_annotations_v2.5.json` (~840 tasks)

### 4. Fix JSON Paths for Test

```powershell
.\python.exe ..\..\yolo-bat-detection\fix_label_studio_paths.py `
  C:\Annotations\test_annotations_v2.5.json `
  C:\Annotations\test_annotations_v2.5_fixed.json `
  test/images
```

**Critical:** Use `test/images` prefix (not just `test`)

### 5. Create New Label Studio Projects

**Option A: Create Two Separate Projects (Recommended)**
- Project 1: "Bat Detection - Validation Set"
- Project 2: "Bat Detection - Test Set"

**Option B: Use Same Training Project**
- Import all JSONs into same project (will merge)

### 6. Import to Label Studio

**For Validation Project:**
1. Start Label Studio: `C:\dm\ai-service\start_label_studio.ps1`
2. Create new project: "Bat Detection - Validation Set"
3. Settings → Cloud Storage → Add Source Storage
   - Storage Type: Local files
   - Absolute local path: `C:\Annotations\valid`
   - File Filter Regex: `.*\.(jpg|png|jpeg)$`
4. Import tasks: `C:\Annotations\valid_annotations_v2.5_fixed.json`
5. Verify first image loads correctly

**For Test Project:**
1. Create new project: "Bat Detection - Test Set"
2. Settings → Cloud Storage → Add Source Storage
   - Storage Type: Local files
   - Absolute local path: `C:\Annotations\test`
   - File Filter Regex: `.*\.(jpg|png|jpeg)$`
3. Import tasks: `C:\Annotations\test_annotations_v2.5_fixed.json`
4. Verify first image loads correctly

### 7. Annotation Tips

**Speed Optimization:**
- v2.5 pre-annotations should be decent quality
- Focus on correcting poor boxes rather than creating from scratch
- Estimate: 2-3 seconds per image → 8-10 hours total

**Quality Checks:**
- Every 100 images, spot-check 5 random annotations
- Look for: tight boxes, no missed bats, no false positives
- Be consistent with training set style

**Common Issues:**
- ❌ Image not loading → Check JSON path has `valid/images/` or `test/images/`
- ❌ No pre-annotations → Confidence too high (try 0.10)
- ❌ Multiple boxes → Delete lower confidence box

### 8. Export Annotations (After Completion)

**From Label Studio UI:**
1. Select all tasks
2. Export → YOLO
3. Save to Downloads

**Move to correct location:**
```powershell
# For validation
Move-Item *.txt C:\Annotations\valid\labels\

# For test
Move-Item *.txt C:\Annotations\test\labels\
```

### 9. Validate Before Training

```powershell
cd C:\dm\ai-service\venv\Scripts
.\python.exe ..\..\yolo-bat-detection\scripts\annotation\validate_dataset.py `
  --dataset-root C:\Annotations `
  --data C:\Annotations\data.yaml
```

**Expected output:**
- ✅ Found 3,650 train images with labels
- ✅ Found 839 valid images with labels
- ✅ Found 840 test images with labels
- ✅ All bounding boxes within valid range

## Checklist Before Starting

- [ ] Training set complete (3,650 annotations)
- [ ] Label Studio running (`start_label_studio.ps1`)
- [ ] Environment variables set (LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true)
- [ ] v2.5 model exists at correct path
- [ ] Backup of training annotations (just in case)

## Timeline Estimate

- Generate pre-annotations (valid + test): ~10 minutes
- Fix JSON paths: ~2 minutes
- Set up Label Studio projects: ~10 minutes
- **Annotate validation (839)**: ~4-5 hours
- **Annotate test (840)**: ~4-5 hours
- Export and validate: ~15 minutes

**Total: ~9-11 hours of annotation work**

## After Annotation Complete

1. Export all labels to YOLO format
2. Update `data.yaml` to uncomment val/test paths
3. Run dataset validation
4. Train v3 model with optimized settings
5. Celebrate with proper mAP metrics! 🎉
