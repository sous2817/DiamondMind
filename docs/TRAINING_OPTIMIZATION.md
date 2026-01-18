# YOLO Training Performance Optimization Guide

## Current Performance Issue (v2.5)
- **Training time:** ~15 min/epoch
- **Total time:** ~12.5 hours for 50 epochs
- **Bottlenecks:**
  1. Validation scanning 839 unlabeled images every epoch
  2. Batch size too small (16) - underutilizes GPU
  3. Only 2 workers - slow data loading
  4. No RAM caching - disk I/O on every epoch
  5. Heavy data augmentation

## Optimizations Applied

### 1. **Increased Batch Size: 16 → 32**
- **Impact:** 2x better GPU utilization
- **Expected speedup:** ~30-40% faster
- **RAM cost:** ~2GB more (you have 5.4GB GPU RAM available)

### 2. **Enabled RAM Caching**
```python
cache=True  # Was: cache=False
```
- **Impact:** Images cached in RAM after first epoch
- **Expected speedup:** ~50% faster after epoch 1
- **RAM cost:** ~10GB system RAM for 5,596 images
- **Result:** Epoch 1 slow (scanning), Epochs 2-50 FAST

### 3. **Increased Workers: 2 → 8**
- **Impact:** Parallel data loading
- **Expected speedup:** ~20-30% faster
- **No RAM cost**

### 4. **Reduced Augmentation**
- Disabled mixup (slow, marginal benefit)
- Reduced mosaic intensity (1.0 → 0.8)
- Reduced color augmentation slightly
- **Expected speedup:** ~10-15% faster
- **Model quality:** Negligible impact with 5,596 images

### 5. **Fixed data.yaml Validation**
```yaml
# Comment out val/test if they don't have labels yet
# val: valid/images  # ← Commented out
```
- **Impact:** No wasted time scanning unlabeled validation images
- **Expected speedup:** Saves 45 seconds per epoch = 37.5 min total

## Expected v3 Training Performance

### Before Optimizations (Current v2.5):
- ~15 min/epoch × 50 epochs = **12.5 hours**

### After Optimizations (Future v3):
- Epoch 1: ~10 min (initial cache creation)
- Epochs 2-50: ~3-4 min each
- **Total: ~3-3.5 hours** 🎯

### Performance Breakdown:
```
Optimization          | Time Saved | Cumulative
---------------------|------------|------------
Batch size 32        | 30%        | 8.75 hrs → 6.13 hrs
RAM caching          | 50%        | 6.13 hrs → 3.06 hrs
Workers 8            | 20%        | 3.06 hrs → 2.45 hrs
Skip val scanning    | 37.5 min   | 2.45 hrs → 1.83 hrs
Reduced augmentation | 10%        | 1.83 hrs → 1.65 hrs
```

**Final estimate: ~2-3 hours for v3 training** (vs 12.5 hours current)

## Additional Tips for v3 Training

### 1. **Before Training:**
```powershell
# Prevent system sleep
powercfg /change standby-timeout-ac 0

# Close unnecessary apps
# - Chrome tabs
# - NZXT CAM
# - Other GPU apps
```

### 2. **Monitor GPU Usage:**
```powershell
# Watch GPU utilization in real-time
nvidia-smi -l 1
```
Target: 70-90% GPU utilization

### 3. **Use Optimized data.yaml:**
```powershell
# Copy the optimized template
cp data_optimized.yaml C:/Annotations/data.yaml
```

### 4. **Optimal Training Command:**
```powershell
python scripts/training/train.py \
  --data C:/Annotations/data.yaml \
  --epochs 50 \
  --batch 32 \
  --device 0 \
  --name v3_final_5596imgs
```

## Hardware Utilization Targets

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| GPU Memory | 5.4GB | 5.8GB | ⬆️ Increase batch |
| GPU Util % | 32% | 75-90% | ⬆️ Bigger batches |
| RAM Usage | ~8GB | 18GB | ✅ Room for cache |
| Workers | 2 | 8 | ⬆️ More parallel |

## Troubleshooting

### "CUDA out of memory"
- Reduce batch size to 24 or 16
- You have 6GB GPU RAM, should handle 32 fine

### "System RAM full"
- Disable cache: `cache=False`
- Close background apps
- You need ~18GB total for caching 5,596 images

### Still slow?
- Check nvidia-smi during training
- GPU util should be 70%+
- If not, increase batch size further (40, 48)

## Summary

**For v3 training (5,596 images):**
- ✅ Use optimized script (batch 32, cache, workers 8)
- ✅ Use optimized data.yaml (no empty validation)
- ✅ Prevent system sleep
- ✅ Close background apps
- 🎯 **Expected time: 2-3 hours** (vs 12.5 hours current)

This is a **4-6x speedup** with no new hardware! 🚀
