import os
import json
import glob
import argparse
import re
import datetime

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
        import sys
        sys.path.append(os.path.dirname(__file__))
        import format_json
        json_str = format_json.format_car_profile(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
        return True
    return False

def log_file(filepath, label, log_dir):
    """Snapshot current RPM data into a persistent log file."""
    try:
        data, _ = load_jsonc(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    led_rpms = data.get("ledRpm", [])
    if not led_rpms:
        return False

    # Derive car name from the source filename (e.g. "hyper-ferrari-499p-2023")
    car_name = os.path.splitext(os.path.basename(filepath))[0]
    if car_name.endswith(".jsonc"):
        car_name = car_name[:-6]

    log_path = os.path.join(log_dir, f"{car_name}.log")

    # Build the new entry
    lines = []
    lines.append(f"--- {label} ---")
    lines.append(f"  captured: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    for gear_obj in led_rpms:
        base_keys = [k for k in gear_obj.keys()
                     if not k.startswith("__COMMENT_") and not k.startswith("//")]

        # Real RPM values
        for k in base_keys:
            arr = gear_obj[k]
            vals = ",".join(str(v) for v in arr)
            lines.append(f'  "{k}": [{vals}]')

        lines.append("")  # blank separator

        # Relative percentages
        for k in base_keys:
            arr = gear_obj[k]
            if not arr or not isinstance(arr[0], (int, float)):
                continue
            baseline = float(arr[0])
            if baseline == 0:
                continue
            precision = get_minimum_precision(arr)
            fmt = f"{{:.{precision}f}}"
            pcts = ",".join(fmt.format(v / baseline) for v in arr)
            lines.append(f'  "{k}": [{pcts}]')

    new_entry = "\n".join(lines) + "\n"

    # Read existing log (if any), preserving the header line
    header = f"# {car_name}\n"
    existing_body = ""
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Strip the header if present
        if content.startswith(header):
            existing_body = content[len(header):]
        else:
            existing_body = content

    os.makedirs(log_dir, exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(new_entry)
        if existing_body:
            f.write("\n")
            f.write(existing_body)

    return True


def main():
    parser = argparse.ArgumentParser(description="Manage RPM shadow comment tables.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--add", action="store_true", help="Add shadow tables where missing")
    group.add_argument("--refresh", action="store_true", help="Recalculate all shadow tables")
    group.add_argument("--remove", action="store_true", help="Remove all shadow tables")
    group.add_argument("--log", metavar="LABEL", type=str,
                       help="Snapshot current RPM data into log files with the given label")

    args = parser.parse_args()

    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src_data", "lmu")
    files = glob.glob(os.path.join(src_dir, "*.jsonc"))

    if args.log:
        log_dir = os.path.join(src_dir, "log")
        logged = 0
        for filepath in files:
            if log_file(filepath, args.log, log_dir):
                logged += 1
        print(f"Logged {logged} files with label '{args.log}' to {log_dir}")
        return

    mode = "add"
    if args.refresh:
        mode = "refresh"
    elif args.remove:
        mode = "remove"

    modified_count = 0
    for filepath in files:
        if process_file(filepath, mode):
            modified_count += 1

    print(f"Successfully processed {len(files)} files, modified {modified_count}.")

if __name__ == "__main__":
    main()
