import json
import re

def format_car_profile(data):
    # Enforce original key order
    original_key_order = ["carName", "carId", "carClass", "ledNumber", "redlineBlinkInterval", "ledColor", "ledRpm"]
    ordered_data = {}
    
    version = data.get("_schemaVersion", "v2.0.0")
    
    if "_schemaVersion" in data:
        ordered_data["_schemaVersion"] = version
        
    # Extract redline aliases (only valid in vHH3.0)
    redline_keys = []
    if version == "vHH3.0":
        redline_keys = sorted([k for k in data if re.match(r'^redline\d+$', k)])
    
    for k in original_key_order:
        if k == "ledColor":
            # Insert redline aliases just before ledColor
            for rk in redline_keys:
                ordered_data[rk] = data[rk]
        if k in data:
            ordered_data[k] = data[k]
            
    for k in data:
        if k not in ordered_data:
            ordered_data[k] = data[k]

    # First dump with standard indent=2
    json_str = json.dumps(ordered_data, indent=2, ensure_ascii=False)
    
    # Compress redlineBlinkInterval array
    def compress_blink_interval(match):
        prefix = match.group(1)
        values = re.findall(r'-?\d+', match.group(2))
        return prefix + '[' + ','.join(values) + ']'
        
    json_str = re.sub(r'("redlineBlinkInterval":\s*)\[([^\]]*)\]', lambda m: compress_blink_interval(m), json_str)

    # Compress ledColor and redline aliases arrays
    def compress_led_color(match):
        prefix = match.group(1)
        values = re.findall(r'"[^"]*"', match.group(2))
        return prefix + '[' + ','.join(values) + ']'
    
    json_str = re.sub(r'("(?:ledColor|redline\d+)":\s*)\[([^\]]*)\]', lambda m: compress_led_color(m), json_str)
    
    # Compress ledRpm gear arrays and convert shadow tables to true comments
    def compress_rpm(match):
        newline = match.group(1)
        spaces = match.group(2)
        is_comment = match.group(3)
        key_name = match.group(4)
        inner = match.group(5)
        
        values = re.findall(r'"[^"]*"|-?\d+\.?\d*', inner)
        compressed = '[' + ','.join(values) + ']'
        
        if is_comment:
            # Convert to a true JSONC comment
            return f'{newline}{spaces}// "{key_name}": {compressed}'
        else:
            return f'{newline}{spaces}"{key_name}": {compressed}'
        
    json_str = re.sub(r'(^|\n)(\s*)"(__COMMENT_)?([R|N|1|2|3|4|5|6|7|8])":\s*\[([^\]]*)\]', lambda m: compress_rpm(m), json_str)
    
    # Compress generator objects back to single lines
    def compress_generator(match):
        newline = match.group(1)
        spaces = match.group(2)
        key_name = match.group(3)
        inner = match.group(4)
        compressed_inner = re.sub(r'\s+', ' ', inner).strip()
        return f'{newline}{spaces}"{key_name}": {{ {compressed_inner} }}'
        
    json_str = re.sub(r'(^|\n)(\s*)"([R|N|1|2|3|4|5|6|7|8])":\s*\{\s*([^}]*?)\s*\}', lambda m: compress_generator(m), json_str)
    
    # Strip any illegal trailing commas caused by converting properties to comments at the end of objects
    json_str = re.sub(r',(\s*(?://[^\n]*\s*)*\})', r'\1', json_str)
    
    return json_str + "\n"

if __name__ == "__main__":
    import sys
    import glob
    import json
    
    def load_jsonc_data(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'\s*//.*$', '', content, flags=re.MULTILINE)
        return json.loads(content)

    for arg in sys.argv[1:]:
        for filepath in glob.glob(arg):
            try:
                data = load_jsonc_data(filepath)
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")
                continue
                
            json_str = format_car_profile(data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
