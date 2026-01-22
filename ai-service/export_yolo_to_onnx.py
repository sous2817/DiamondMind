"""
Export YOLO v3 model to ONNX format for memory optimization
"""
from ultralytics import YOLO
import os

# Load PyTorch model
model_path = 'yolo-bat-detection/models/v3_full_5329imgs/best.pt'
print(f"Loading YOLO model from: {model_path}")
model = YOLO(model_path)

# Export to ONNX
print("Exporting to ONNX format...")
model.export(
    format='onnx',
    simplify=True,  # Simplify ONNX graph for better performance
    opset=12  # ONNX opset version (12 is widely supported)
)

print("✅ Export complete!")
print("ONNX model created: best.onnx")
print("\nNext step: Move best.onnx to production folder")
