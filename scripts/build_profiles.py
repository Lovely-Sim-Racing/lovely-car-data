import os
import json
import re

def compress_json_arrays(json_str):
    # This regex finds arrays of primitives (numbers, strings) and compresses them to a single line
    # It works by matching [ followed by numbers/strings/whitespace/commas and ]
    # A safer way is to just use a custom encoder or simple string replacements for the specific arrays we know.
    # Since we know our schema, the arrays that need compressing are `ledColor` and the arrays inside `ledRpm`.
    
    # We can just collapse any array that doesn't contain '{' or '[' (no nested objects/arrays)
    def replacer(match):
        # Remove newlines and extra spaces
        content = match.group(0)
        content = re.sub(r'\s+', '', content)
        # Add space after comma for readability if desired, though upstream might not have it
        return content

    # Regex to match arrays containing only numbers, strings, and commas
    # This is a bit tricky with regex. Let's do it procedurally or with a simpler regex.
    # Match [ ... ] containing only "...", numbers, commas, and whitespace
    compressed = re.sub(r'\[\s*(?:(?:\"[^\"]*\"|-?\d+)\s*,\s*)*(?:\"[^\"]*\"|-?\d+)?\s*\]', replacer, json_str)
    return compressed

def build_profiles(src_base_dir, out_base_dir):
    # For now, we only process lmu, but can be expanded
    src_dir = os.path.join(src_base_dir, 'lmu')
    out_dir = os.path.join(out_base_dir, 'lmu')
    
    if not os.path.exists(src_dir):
        print(f"Source directory {src_dir} does not exist.")
        return
        
    os.makedirs(out_dir, exist_ok=True)
    
    generated_files = []
    
    for filename in os.listdir(src_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(src_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                template_data = json.load(f)
            except Exception as e:
                print(f"Error parsing {filename}: {e}")
                continue
                
        variants = template_data.pop('variants', [])
        
        for variant in variants:
            # Create a copy of the template data
            profile_data = template_data.copy()
            
            # Inject variant specific fields
            final_data = {}
            if "carName" in variant:
                final_data["carName"] = variant["carName"]
            if "carId" in variant:
                final_data["carId"] = variant["carId"]
                
            # Copy all other fields from template
            for k, v in profile_data.items():
                final_data[k] = v
                
            out_filename = variant.get("fileName")
            if not out_filename:
                continue
                
            out_filepath = os.path.join(out_dir, out_filename)
            
            json_str = json.dumps(final_data, indent=2, ensure_ascii=False)
            json_str = compress_json_arrays(json_str)
            
            with open(out_filepath, 'w', encoding='utf-8') as f:
                f.write(json_str + "\n")
                
            generated_files.append(out_filepath)
            
    print(f"Successfully built {len(generated_files)} profiles in {out_dir}")

if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_base_dir = os.path.join(project_root, 'src_data')
    out_base_dir = os.path.join(project_root, 'data')
    
    build_profiles(src_base_dir, out_base_dir)
