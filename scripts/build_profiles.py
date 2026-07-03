import os
import json
import re

def load_jsonc(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Strip true comments (//) before parsing
    content = re.sub(r'\s*//.*$', '', content, flags=re.MULTILINE)
    return json.loads(content)

def build_profiles(src_base_dir, out_base_dir):
    # For now, we only process lmu, but can be expanded
    src_dir = os.path.join(src_base_dir, 'lmu')
    out_dir = os.path.join(out_base_dir, 'lmu')
    
    if not os.path.exists(src_dir):
        print(f"Source directory {src_dir} does not exist.")
        return
        
    import shutil
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    generated_files = []
    
    # Process all JSONC files in the source directory
    for filename in os.listdir(src_dir):
        if not filename.endswith('.jsonc'):
            continue
            
        filepath = os.path.join(src_dir, filename)
        try:
            template_data = load_jsonc(filepath)
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            continue
                
        variants = template_data.pop('variants', [])
        
        for variant in variants:
            final_data = {}
            # Copy all fields from template first
            for k, v in template_data.items():
                final_data[k] = v
                
            # Inject variant specific fields (overriding template)
            for k, v in variant.items():
                if k != "fileName":
                    final_data[k] = v
                
            # Process ledRpm generators and strip mock comment keys
            if "ledRpm" in final_data:
                led_count = final_data.get("ledNumber", 10)
                for gear_obj in final_data["ledRpm"]:
                    keys_to_remove = [k for k in gear_obj.keys() if k.startswith("//")]
                    for k in keys_to_remove:
                        del gear_obj[k]
                    for k, v in gear_obj.items():
                        if isinstance(v, dict) and "redline" in v and "step" in v:
                            redline = v["redline"]
                            step = v["step"]
                            new_array = [redline]
                            for i in range(1, led_count + 1):
                                val = int(round(redline - (led_count - i) * step))
                                new_array.append(val)
                            gear_obj[k] = new_array
                
            out_filename = variant.get("fileName")
            if not out_filename:
                continue
                
            out_filepath = os.path.join(out_dir, out_filename)
            
            # Use the custom formatter to keep ledColor and ledRpm inline
            import format_json
            json_str = format_json.format_car_profile(final_data)
            
            with open(out_filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
                
            generated_files.append(out_filepath)
            
    print(f"Successfully built {len(generated_files)} profiles in {out_dir}")

if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_base_dir = os.path.join(project_root, 'src_data')
    out_base_dir = os.path.join(project_root, 'data')
    
    build_profiles(src_base_dir, out_base_dir)
