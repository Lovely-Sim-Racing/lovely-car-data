import os
import json

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
            
            # The repo's pre-commit script uses pretty-format-json --no-sort-keys 
            # which formats with indent=2, expands all arrays, and uses ensure_ascii=True.
            # We use indent=2 and add a trailing newline to match it exactly.
            json_str = json.dumps(final_data, indent=2)
            
            with open(out_filepath, 'w', encoding='utf-8') as f:
                f.write(json_str + "\n")
                
            generated_files.append(out_filepath)
            
    print(f"Successfully built {len(generated_files)} profiles in {out_dir}")

if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_base_dir = os.path.join(project_root, 'src_data')
    out_base_dir = os.path.join(project_root, 'data')
    
    build_profiles(src_base_dir, out_base_dir)
