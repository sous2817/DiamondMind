"""
Convert YOLOv8 Polygon/Segmentation annotations to Bounding Boxes

This script converts annotation files from polygon/segmentation format 
(many x,y coordinate pairs) to regular YOLO bounding box format.

Usage:
    python convert_polygon_to_bbox.py
"""

import os
from pathlib import Path

def convert_polygon_to_bbox(polygon_coords):
    """
    Convert polygon coordinates to axis-aligned bounding box.
    
    Args:
        polygon_coords: List of coordinate pairs [x1, y1, x2, y2, ..., xn, yn]
    
    Returns:
        List of 4 values [x_center, y_center, width, height] (normalized 0-1)
    """
    # Extract x and y coordinates
    x_coords = [polygon_coords[i] for i in range(0, len(polygon_coords), 2)]
    y_coords = [polygon_coords[i] for i in range(1, len(polygon_coords), 2)]
    
    # Calculate bounding box
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
    Convert a single label file from polygon to bbox format.
    
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
            
            if len(parts) < 5:
                print(f"   ⚠️  Skipping invalid line in {label_path.name}")
                continue
            
            class_id = parts[0]
            coords = [float(x) for x in parts[1:]]
            
            # Check if already in bbox format (4 values)
            if len(coords) == 4:
                converted_lines.append(line)
                continue
            
            # Check if it's polygon/segmentation (even number of coords)
            if len(coords) % 2 != 0:
                print(f"   ⚠️  Odd number of coordinates in {label_path.name}")
                return False
            
            # Convert polygon to bbox
            bbox = convert_polygon_to_bbox(coords)
            
            # Format: class x_center y_center width height
            converted_line = f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n"
            converted_lines.append(converted_line)
        
        # Write converted labels back
        with open(label_path, 'w') as f:
            f.writelines(converted_lines)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error converting {label_path.name}: {e}")
        return False


def convert_dataset(dataset_dir='dataset'):
    """
    Convert all label files in the dataset from polygon to bbox format.
    
    Args:
        dataset_dir: Root directory of the dataset
    """
    print("🔄 Converting Polygon/Segmentation to Bounding Boxes...")
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
