import os
import csv
import hashlib
from PIL import Image

def get_pixel_hash(image_path):
    """Opens an image, extracts raw pixel data, and returns its MD5 hash."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB to normalize grayscale/RGBA differences
            img = img.convert('RGB')
            # Extract raw bytes of the pixels
            pixel_bytes = img.tobytes()
            # Generate MD5 hash of the pixels
            return hashlib.md5(pixel_bytes).hexdigest()
    except Exception as e:
        # Skips corrupted files or non-image files like .DS_Store
        return None

def check_pixel_leakage(root_dir, output_csv="pixel_leakage_report.csv"):
    folds_dir = os.path.join(root_dir, "FOLDS")
    report = []
    
    if not os.path.exists(folds_dir):
        print(f"Error: Could not find 'FOLDS' directory in {root_dir}")
        return

    folds = [f for f in os.listdir(folds_dir) if f.startswith('fold')]
    
    for fold in sorted(folds):
        print(f"Analyzing {fold} at pixel level...")
        fold_path = os.path.join(folds_dir, fold)
        sets = ['Train', 'Test', 'Valid']
        
        # Key: pixel_hash, Value: list of dicts containing metadata
        hash_map = {}

        for s in sets:
            set_path = os.path.join(fold_path, s)
            if not os.path.exists(set_path):
                continue
            
            for root, dirs, files in os.walk(set_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        full_path = os.path.join(root, file)
                        
                        # Compute pixel-level hash
                        img_hash = get_pixel_hash(full_path)
                        if not img_hash:
                            continue
                            
                        if img_hash not in hash_map:
                            hash_map[img_hash] = []
                            
                        hash_map[img_hash].append({
                            'set': s,
                            'filename': file,
                            'path': full_path
                        })

        # Process the hashes to find split violations within this fold
        for img_hash, occurrences in hash_map.items():
            if len(occurrences) > 1:
                # Check if the duplicate pixels are split across Train, Test, or Valid
                distinct_sets = set([occ['set'] for occ in occurrences])
                
                if len(distinct_sets) > 1:
                    # Construct clean diagnostic strings for the CSV
                    details = [f"{occ['set']} -> {occ['filename']}" for occ in occurrences]
                    paths = [occ['path'] for occ in occurrences]
                    
                    report.append({
                        "Fold": fold,
                        "Pixel MD5 Hash": img_hash,
                        "Leaked Across": " | ".join(details),
                        "Full System Paths": " | ".join(paths)
                    })

    # Export to CSV
    if report:
        keys = report[0].keys()
        with open(output_csv, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(report)
        print(f"\n⚠️ Pixel-level leakage detected! Report saved to: {output_csv}")
    else:
        print("\n✅ Clean split! No pixel-identical duplicate images found across your sets.")

if __name__ == "__main__":
    current_directory = os.getcwd()
    check_pixel_leakage(current_directory)