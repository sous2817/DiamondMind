"""
Convert YOLOv8 Oriented Bounding Boxes (OBB) to Regular Bounding Boxes

This script converts annotation files from OBB format (4 corner points) 
to regular YOLO bounding box format (center x, y, width, height).

Usage:
    python convert_obb_to_bbox.py
"""

import os
from pathlib import Path
import numpy as np

def convert_obb_to_bbox(obb_coords):
    """
    Convert oriented bounding box coordinates to axis-aligned bounding box.
    
    Args:
        obb_coords: List of 8 values [x1, y1, x2, y2, x3, y3, x4, y4]
    
    Returns:
        List of 4 values [x_center, y_center, width, height] (normalized 0-1)
    """
    # Extract the 4 corner points
    x1, y1, x2, y2, x3, y3, x4, y4 = obb_coords
    
    # Get all x and y coordinates
    x_coords = [x1, x2, x3, x4]
    y_coords = [y1, y2, y3, y4]
    
    # Calculate axis-aligned bounding box
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    # Calculate center, width, height (already normalized 0-1)
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min
    
    return [x_center, y_center, width, height]


def convert_label_file(label_path):
    """
    Convert a single label file from OBB to bbox format.
    
    Args:
        label_path: Path to the label file
    
    Returns:
        bool: True if converted successfully, False otherwise
    """
    try:
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        converted_lines = []
        for line in lines:
            parts = line.strip().split()
            
            # Check if it's OBB format (class + 8 coordinates = 9 values)
            if len(parts) == 9:
                class_id = parts[0]
                obb_coords = [float(x) for x in parts[1:]]
                
                # Convert to bbox
                bbox = convert_obb_to_bbox(obb_coords)
                
                # Format: class x_center y_center width height
                converted_line = f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n"
                converted_lines.append(converted_line)
                
            elif len(parts) == 5:
                # Already in correct format
                converted_lines.append(line)
                
            else:
                print(f"   ⚠️  Unexpected format ({len(parts)} values): {label_path.name}")
                return False
        
        # Write converted labels back
        with open(label_path, 'w') as f:
            f.writelines(converted_lines)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error converting {label_path.name}: {e}")
        return False


def convert_dataset(dataset_dir='dataset'):
    """
    Convert all label files in the dataset from OBB to bbox format.
    
    Args:
        dataset_dir: Root directory of the dataset
    """
    print("🔄 Converting OBB to Regular Bounding Boxes...")
    print("=" * 50)
    
    dataset_path = Path(dataset_dir)
    splits = ['train', 'valid', 'test']
    
    total_converted = 0
    total_files = 0
    
    for split in splits:
        labels_dir = dataset_path / split / 'labels'
        
        if not labels_dir.exists():
            print(f"⚠️  {split}/labels not found, skipping...")
            continue
        
        label_files = list(labels_dir.glob('*.txt'))
        print(f"\n📂 {split.upper()} Split: {len(label_files)} files")
        
        converted = 0
        for label_file in label_files:
            if convert_label_file(label_file):
                converted += 1
        
        print(f"   ✅ Converted: {converted}/{len(label_files)}")
        total_converted += converted
        total_files += len(label_files)
    
    print("\n" + "=" * 50)
    print(f"✅ Conversion Complete!")
    print(f"   Total: {total_converted}/{total_files} files converted")
    
    if total_converted == total_files:
        print("\n🎉 All files converted successfully!")
        print("   Run: python scripts/validate.py --check-dataset")
    else:
        print(f"\n⚠️  {total_files - total_converted} files had issues")


if __name__ == '__main__':
    convert_dataset()
