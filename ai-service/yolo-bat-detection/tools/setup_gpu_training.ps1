# Setup GPU Training for YOLO Bat Detection
# This script installs CUDA-enabled PyTorch and verifies GPU availability

Write-Host "🎮 Setting up GPU Training for YOLO..." -ForegroundColor Cyan
Write-Host "=" * 50

# Step 1: Check for NVIDIA GPU
Write-Host "`n📊 Checking for NVIDIA GPU..." -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>$null
    if ($gpuInfo) {
        Write-Host "✅ GPU detected: $gpuInfo" -ForegroundColor Green
    } else {
        Write-Host "❌ No NVIDIA GPU found. GPU training not available." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ nvidia-smi not found. Make sure NVIDIA drivers are installed." -ForegroundColor Red
    exit 1
}

# Step 2: Activate virtual environment
Write-Host "`n🔧 Activating virtual environment..." -ForegroundColor Yellow
Set-Location "c:\dm\ai-service"
& .\venv\Scripts\Activate.ps1

# Step 3: Uninstall CPU-only PyTorch
Write-Host "`n🗑️  Uninstalling CPU-only PyTorch..." -ForegroundColor Yellow
pip uninstall torch torchvision torchaudio -y

# Step 4: Install CUDA-enabled PyTorch
Write-Host "`n⬇️  Installing CUDA-enabled PyTorch (CUDA 12.1)..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Step 5: Verify GPU support
Write-Host "`n✅ Verifying GPU support..." -ForegroundColor Yellow
python -c @"
import torch
print('=' * 50)
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'GPU Count: {torch.cuda.device_count()}')
    print(f'GPU Name: {torch.cuda.get_device_name(0)}')
    print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
    print('=' * 50)
    print('✅ GPU training is ready!')
else:
    print('❌ GPU not detected. Check installation.')
print('=' * 50)
"@

# Step 6: Prompt for training
Write-Host "`n🎯 Ready to train!" -ForegroundColor Green
Write-Host "`nTo start training with GPU:" -ForegroundColor Cyan
Write-Host "  cd yolo-bat-detection" -ForegroundColor White
Write-Host "  python scripts\train.py --epochs 50 --batch 16 --device 0" -ForegroundColor White
Write-Host "`nExpected training time: ~5-10 minutes (vs 30-60 min on CPU)" -ForegroundColor Gray
Write-Host "`nPress Enter to start training now, or Ctrl+C to exit..."
Read-Host

# Step 7: Start training
Write-Host "`n🚀 Starting GPU training..." -ForegroundColor Green
Set-Location "yolo-bat-detection"
python scripts\train.py --epochs 50 --batch 16 --device 0
