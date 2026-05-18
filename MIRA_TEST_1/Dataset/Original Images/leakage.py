import os
import csv

def check_data_leakage(root_dir, output_csv="data_leakage_report.csv"):
    folds_dir = os.path.join(root_dir, "FOLDS")
    
    # List to store results: [Fold, Image Name, Found In]
    report = []
    
    if not os.path.exists(folds_dir):
        print(f"Error: Could not find 'FOLDS' directory in {root_dir}")
        return

    # Get fold folders (fold1, fold2, etc.)
    folds = [f for f in os.listdir(folds_dir) if f.startswith('fold')]
    
    for fold in sorted(folds):
        fold_path = os.path.join(folds_dir, fold)
        sets = ['Train', 'Test', 'Valid']
        
        # Dictionary to store filenames and their full paths
        # Key: filename, Value: list of paths where it exists in this fold
        file_map = {}

        for s in sets:
            set_path = os.path.join(fold_path, s)
            if not os.path.exists(set_path):
                continue
            
            # Walk through subdirectories (Chickenpox, Cowpox, etc.)
            for root, dirs, files in os.walk(set_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        full_path = os.path.join(root, file)
                        if file not in file_map:
                            file_map[file] = []
                        file_map[file].append(f"{s} ({full_path})")

        # Identify duplicates in this specific fold
        for filename, locations in file_map.items():
            if len(locations) > 1:
                # Check if they are in different sets (Train vs Test vs Valid)
                # We extract the set name from the beginning of our custom string
                found_sets = set([loc.split(' ')[0] for loc in locations])
                
                if len(found_sets) > 1:
                    report.append({
                        "Fold": fold,
                        "Image Name": filename,
                        "Conflict Locations": " | ".join(locations)
                    })

    # Writing to CSV
    if report:
        keys = report[0].keys()
        with open(output_csv, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(report)
        print(f"✅ Leakage found! Report saved to: {output_csv}")
    else:
        print("✅ Success! All images in each fold are distinct across Train, Test, and Valid sets.")

if __name__ == "__main__":
    # Point this to your 'Original Images' directory
    current_directory = os.getcwd()
    check_data_leakage(current_directory)