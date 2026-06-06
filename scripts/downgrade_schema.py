import os
import json
import re

def load_jsonc(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Strip comments
    content = re.sub(r'^\s*//.*$', '', content, flags=re.MULTILINE)
    return json.loads(content)

def downgrade_car_profile(data):
    # Enforce original key order
    original_key_order = ["carName", "carId", "carClass", "ledNumber", "redlineBlinkInterval", "ledColor", "ledRpm"]
    downgraded = {}
    
    # Copy basic attributes
    for k in original_key_order:
        if k in data:
            downgraded[k] = data[k]
            
    # Copy any extra attributes
    for k in data:
        if k not in downgraded:
            downgraded[k] = data[k]
            
    # 1. Handle Multi-Redline (e.g., Corvette GT3)
    # The original schema expects len(ledColor) == ledNumber + 1
    # Our fork has len(ledColor) == ledNumber + 2 (because of the extra redline value inserted at index 1)
    led_number = downgraded.get("ledNumber")
    led_color = downgraded.get("ledColor", [])
    
    has_multi_redline = False
    if led_number is not None and len(led_color) == led_number + 2:
        has_multi_redline = True
        # Remove the extra redline color at index 1
        new_color = list(led_color)
        del new_color[1]
        downgraded["ledColor"] = new_color
        
    # 2. Process ledRpm
    if "ledRpm" in downgraded and isinstance(downgraded["ledRpm"], list) and len(downgraded["ledRpm"]) > 0:
        gear_obj = downgraded["ledRpm"][0]
        
        # If we had multi-redline, we need to remove the corresponding index 1 value from each gear's RPM array
        if has_multi_redline:
            new_gear_obj = {}
            for gear, rpms in gear_obj.items():
                if isinstance(rpms, list) and len(rpms) == led_number + 2:
                    new_rpms = list(rpms)
                    del new_rpms[1]
                    new_gear_obj[gear] = new_rpms
                else:
                    new_gear_obj[gear] = rpms
            gear_obj = new_gear_obj
            downgraded["ledRpm"][0] = gear_obj
            
        # We don't force fill gears up to 8 anymore, because the original repository was inconsistent (some cars had 8, some had 6).
        # We leave the gears as defined in the fork template.
                    
    return downgraded

def format_car_profile(data):
    # Enforce original key order
    original_key_order = ["carName", "carId", "carClass", "ledNumber", "redlineBlinkInterval", "ledColor", "ledRpm"]
    ordered_data = {}
    for k in original_key_order:
        if k in data:
            ordered_data[k] = data[k]
    for k in data:
        if k not in ordered_data:
            ordered_data[k] = data[k]

    # First dump with standard indent=2
    json_str = json.dumps(ordered_data, indent=2, ensure_ascii=False)
    
    # Compress ledColor array
    def compress_led_color(match):
        prefix = match.group(1)
        values = re.findall(r'"[^"]*"', match.group(2))
        return prefix + '[' + ','.join(values) + ']'
    
    json_str = re.sub(r'("ledColor":\s*)\[([^\]]*)\]', lambda m: compress_led_color(m), json_str)
    
    # Compress ledRpm gear arrays
    def compress_rpm(match):
        newline = match.group(1)
        spaces = match.group(2)
        key_name = match.group(3)
        inner = match.group(4)
        values = re.findall(r'"[^"]*"|-?\d+\.?\d*', inner)
        return f'{newline}{spaces}"{key_name}": [' + ','.join(values) + ']'
        
    json_str = re.sub(r'(^|\n)(\s*)"([R|N|1|2|3|4|5|6|7|8])":\s*\[([^\]]*)\]', lambda m: compress_rpm(m), json_str)
    return json_str + "\n"

def process_directory(src_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for filename in os.listdir(src_dir):
        if not filename.endswith('.json'):
            continue
        src_path = os.path.join(src_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        
        try:
            data = load_jsonc(src_path)
            downgraded = downgrade_car_profile(data)
            json_str = format_car_profile(downgraded)
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python downgrade_schema.py <src_dir> <dest_dir>")
        sys.exit(1)
    process_directory(sys.argv[1], sys.argv[2])
