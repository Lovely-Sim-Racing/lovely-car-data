import os
import json
import glob
import argparse
import re

def load_jsonc(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Strip true comments (//) before parsing
    content = re.sub(r'^\s*//.*$', '', content, flags=re.MULTILINE)
    return json.loads(content), content

def get_minimum_precision(arr, max_decimals=6):
    baseline = float(arr[0])
    if baseline == 0:
        return 4 # fallback
        
    for decimals in range(2, max_decimals + 1):
        success = True
        for val in arr:
            if not isinstance(val, (int, float)):
                continue
            pct = round(val / baseline, decimals)
            reconstructed = round(pct * baseline)
            if reconstructed != val:
                success = False
                break
        if success:
            return decimals
            
    return max_decimals

def process_file(filepath, mode):
    try:
        data, original_content = load_jsonc(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    modified = False
    led_rpms = data.get("ledRpm", [])
    
    for gear_obj in led_rpms:
        # Strip any existing mock comment keys
        keys_to_remove = [k for k in gear_obj.keys() if k.startswith("__COMMENT_") or k.startswith("//")]
        keys = list(gear_obj.keys())
        base_keys = [k for k in keys if not k.startswith("__COMMENT_") and not k.startswith("//")]
        
        if mode == "remove":
            # Just relying on load_jsonc stripping the true comments is enough,
            # but we also clear __COMMENT_ keys if they existed in the loaded data.
            for k in keys_to_remove:
                del gear_obj[k]
                modified = True
            if "//" in original_content:
                modified = True
        
        elif mode in ["add", "refresh"]:
            for k in keys_to_remove:
                del gear_obj[k]
                
            new_gear_obj = {}
            for k in base_keys:
                new_gear_obj[k] = gear_obj[k]
                
            for k in base_keys:
                arr = gear_obj[k]
                if not arr or not isinstance(arr[0], (int, float)):
                    continue
                
                baseline = float(arr[0])
                if baseline == 0:
                    continue
                    
                precision = get_minimum_precision(arr)
                fmt_str = f"{{:.{precision}f}}"
                
                shadow = []
                for val in arr:
                    if not isinstance(val, (int, float)):
                        shadow.append(str(val))
                    else:
                        pct = val / baseline
                        shadow.append(fmt_str.format(pct))
                
                comment_key = f"__COMMENT_{k}"
                new_gear_obj[comment_key] = shadow
                modified = True
                
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
    files = glob.glob(os.path.join(src_dir, "*.jsonc"))
    
    modified_count = 0
    for filepath in files:
        if process_file(filepath, mode):
            modified_count += 1
            
    print(f"Successfully processed {len(files)} files, modified {modified_count}.")

if __name__ == "__main__":
    main()
