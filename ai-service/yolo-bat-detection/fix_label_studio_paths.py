"""
Fix Label Studio JSON paths to include subdirectory
Updates paths from /data/local-files/?d=IMG_*.png 
            to /data/local-files/?d=train/IMG_*.png
"""

import json
import sys

def fix_json_paths(input_file, output_file, subdirectory):
    """Fix paths in Label Studio JSON to include subdirectory"""
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Update each task's image path
    for task in data:
        if 'data' in task and 'image' in task['data']:
            old_path = task['data']['image']
            # Extract filename from path
            if '?d=' in old_path:
                filename = old_path.split('?d=')[-1]
                # Add subdirectory
                new_path = f"/data/local-files/?d={subdirectory}/{filename}"
                task['data']['image'] = new_path
                print(f"Fixed: {filename} -> {subdirectory}/{filename}")
    
    # Save updated JSON
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Fixed {len(data)} tasks")
    print(f"📁 Output: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python fix_label_studio_paths.py input.json output.json subdirectory")
        print("Example: python fix_label_studio_paths.py train_annotations.json train_annotations_fixed.json train")
        sys.exit(1)
    
    fix_json_paths(sys.argv[1], sys.argv[2], sys.argv[3])
