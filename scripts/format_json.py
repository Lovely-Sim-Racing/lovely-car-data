import json
import re

def format_car_profile(data):
    # First dump with standard indent=2
    json_str = json.dumps(data, indent=2)
    
    # Compress ledColor array
    def compress_led_color(match):
        prefix = match.group(1)
        values = re.findall(r'"[^"]*"', match.group(2))
        return prefix + '[' + ','.join(values) + ']'
    
    json_str = re.sub(r'("ledColor":\s*)\[([^\]]*)\]', lambda m: compress_led_color(m), json_str)
    
    # Compress ledRpm gear arrays and shadow tables
    def compress_rpm(match):
        prefix = match.group(2)
        inner = match.group(3)
        # Match both integers, negative integers, strings, floats, and formatted string floats like "1.00"
        values = re.findall(r'"[^"]*"|-?\d+\.?\d*', inner)
        return prefix + '[' + ','.join(values) + ']'
        
    json_str = re.sub(r'(^|\n)(\s*"(?://)?[R|N|1|2|3|4|5|6|7|8]":\s*)\[([^\]]*)\]', lambda m: m.group(1) + compress_rpm(m), json_str)
    
    return json_str + "\n"

if __name__ == "__main__":
    import sys
    import os
    import glob
    
    files = []
    for pattern in sys.argv[1:]:
        files.extend(glob.glob(pattern))
        
    for filepath in files:
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")
                continue
                
        formatted = format_car_profile(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)
