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
        content = re.sub(r'^\s*//.*$', '', content, flags=re.MULTILINE)
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
