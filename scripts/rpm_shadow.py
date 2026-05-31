import os
import json
import glob
import argparse

def process_file(filepath, mode):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return False

    modified = False
    led_rpms = data.get("ledRpm", [])
    
    for gear_obj in led_rpms:
        keys_to_remove = [k for k in gear_obj.keys() if k.startswith("//")]
        keys = list(gear_obj.keys())
        
        # Determine base gear keys (not comments)
        base_keys = [k for k in keys if not k.startswith("//")]
        
        if mode == "remove":
            for k in keys_to_remove:
                del gear_obj[k]
                modified = True
        
        elif mode in ["add", "refresh"]:
            # If refresh, we remove them first to recalculate and reposition
            if mode == "refresh":
                for k in keys_to_remove:
                    del gear_obj[k]
                    
            # We want to insert the comment keys collectively at the bottom
            new_gear_obj = {}
            # First, add all the base keys
            for k in base_keys:
                new_gear_obj[k] = gear_obj[k]
                
            # Then, append the shadow keys below them
            for k in base_keys:
                comment_key = f"//{k}"
                if mode == "add" and comment_key in gear_obj:
                    new_gear_obj[comment_key] = gear_obj[comment_key]
                    continue
                    
                # Calculate shadow
                arr = gear_obj[k]
                if not arr or not isinstance(arr[0], (int, float)):
                    continue
                
                baseline = float(arr[0])
                if baseline == 0:
                    continue
                
                shadow = []
                for val in arr:
                    if not isinstance(val, (int, float)):
                        shadow.append(str(val))
                    else:
                        pct = val / baseline
                        shadow.append(f"{pct:.2f}")
                
                new_gear_obj[comment_key] = shadow
                modified = True
                
            # Replace the gear object with the new ordered one
            gear_obj.clear()
            gear_obj.update(new_gear_obj)

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Manage RPM shadow comment tables.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--add", action="store_true", help="Add shadow tables where missing")
    group.add_argument("--refresh", action="store_true", help="Recalculate all shadow tables")
    group.add_argument("--remove", action="store_true", help="Remove all shadow tables")
    
    args = parser.parse_args()
    
    mode = "add"
    if args.refresh:
        mode = "refresh"
    elif args.remove:
        mode = "remove"
        
    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src_data", "lmu")
    files = glob.glob(os.path.join(src_dir, "*.json"))
    
    modified_count = 0
    for filepath in files:
        if process_file(filepath, mode):
            modified_count += 1
            
    print(f"Successfully processed {len(files)} files, modified {modified_count}.")

if __name__ == "__main__":
    main()
