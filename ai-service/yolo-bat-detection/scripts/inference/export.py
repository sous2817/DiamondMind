"""
YOLOv8 Bat Detection - Model Export Script
DM-53: Create Annotated Dataset for YOLO Bat Detection Model

Export trained model to different formats for deployment.

Usage:
    python export_model.py --format onnx          # ONNX (universal)
    python export_model.py --format torchscript   # PyTorch
    python export_model.py --format tflite        # TensorFlow Lite (mobile)
    python export_model.py --format coreml        # CoreML (iOS)
"""

from ultralytics import YOLO
import argparse
from pathlib import Path

def export_model(
    model_path='runs/detect/bat_detection/weights/best.pt',
    format='onnx',
    imgsz=640
):
    """
    Export YOLOv8 model to different formats.
    
    Args:
        model_path: Path to trained model weights
        format: Export format (onnx, torchscript, tflite, coreml, etc.)
        imgsz: Input image size for export
    """
    print("📦 DiamondMind - Model Export")
    print("=" * 50)
    
    # Check if model exists
    model_path = Path(model_path)
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        print("   Train a model first: python scripts/train.py")
        return
    
    print(f"📥 Loading model: {model_path}")
    model = YOLO(str(model_path))
    
    print(f"🔄 Exporting to {format.upper()} format...")
    print(f"   Image size: {imgsz}")
    
    # Export model
    export_path = model.export(
        format=format,
        imgsz=imgsz,
        half=False,          # FP16 quantization (only for GPU)
        int8=False,          # INT8 quantization
        dynamic=False,       # Dynamic input shape
        simplify=True,       # Simplify ONNX model
        opset=12,            # ONNX opset version
    )
    
    print("\n" + "=" * 50)
    print(f"✅ Export complete!")
    print(f"📁 Exported model: {export_path}")
    
    # Format-specific tips
    if format == 'onnx':
        print("\n💡 ONNX Tips:")
        print("   - Universal format, works with most frameworks")
        print("   - Good for production deployment")
        print("   - Use with ONNX Runtime for fast inference")
    
    elif format == 'torchscript':
        print("\n💡 TorchScript Tips:")
        print("   - Native PyTorch format")
        print("   - Good for Python production environments")
        print("   - Can be loaded without Ultralytics")
    
    elif format == 'tflite':
        print("\n💡 TensorFlow Lite Tips:")
        print("   - Optimized for mobile (Android)")
        print("   - Smaller model size")
        print("   - Faster inference on edge devices")
    
    elif format == 'coreml':
        print("\n💡 CoreML Tips:")
        print("   - Optimized for iOS/macOS")
        print("   - Works with Swift/Obj-C")
        print("   - Hardware acceleration on Apple devices")
    
    print("\n🚀 Next Steps:")
    print("   1. Test exported model with your deployment framework")
    print("   2. Benchmark inference speed")
    print("   3. Integrate into DiamondMind AI service (DM-54)")


def benchmark_formats(model_path='runs/detect/bat_detection/weights/best.pt'):
    """
    Export to multiple formats and compare file sizes.
    """
    print("📊 Benchmarking Export Formats...")
    print("=" * 50)
    
    formats = ['onnx', 'torchscript']  # Common formats
    
    model = YOLO(model_path)
    results = {}
    
    for fmt in formats:
        print(f"\n🔄 Exporting to {fmt}...")
        try:
            export_path = model.export(format=fmt, imgsz=640)
            file_size = Path(export_path).stat().st_size / (1024 * 1024)  # MB
            results[fmt] = {
                'path': export_path,
                'size_mb': file_size
            }
            print(f"   ✅ Size: {file_size:.2f} MB")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Format Comparison:")
    for fmt, info in results.items():
        print(f"   {fmt.upper()}: {info['size_mb']:.2f} MB")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export YOLOv8 Bat Detection Model')
    
    parser.add_argument('--model', type=str,
                        default='runs/detect/bat_detection/weights/best.pt',
                        help='Path to trained model weights')
    parser.add_argument('--format', type=str, default='onnx',
                        choices=['onnx', 'torchscript', 'tflite', 'coreml', 'engine'],
                        help='Export format')
    parser.add_argument('--imgsz', type=int, default=640,
                        help='Input image size')
    parser.add_argument('--benchmark', action='store_true',
                        help='Benchmark multiple export formats')
    
    args = parser.parse_args()
    
    if args.benchmark:
        benchmark_formats(args.model)
    else:
        export_model(args.model, args.format, args.imgsz)
