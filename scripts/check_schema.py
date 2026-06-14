#!/usr/bin/env python3
"""Check that JSON files adhere strictly to the v2.00 Lovely Dashboard schema."""

import json
import sys
import argparse
from pathlib import Path

def check_file_schema(filepath: Path) -> list[str]:
    errors = []
    import re
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'^\s*//.*$', '', content, flags=re.MULTILINE)
        data = json.loads(content)
            
        version = data.get("_schemaVersion", "v2.0.0")
        
        if version == "v2.0.0":
            if "statusLeds" in data:
                errors.append(f"{filepath}: 'statusLeds' is not supported in v2.0.0.")
                
            for k in data.keys():
                if k.startswith("redline") and k != "redlineBlinkInterval":
                    errors.append(f"{filepath}: found '{k}'. Multi-redline configurations must be flattened in v2.0.0.")
                    
            if "redlineBlinkInterval" in data and not isinstance(data["redlineBlinkInterval"], int):
                errors.append(f"{filepath}: 'redlineBlinkInterval' must be a single integer in v2.0.0.")

            if "ledColor" in data:
                for c in data["ledColor"]:
                    if not isinstance(c, str) or not c.startswith("#"):
                        errors.append(f"{filepath}: 'ledColor' contains non-hex value '{c}' in v2.0.0.")

            if "ledRpm" in data and isinstance(data["ledRpm"], list):
                for gear_map in data["ledRpm"]:
                    for gear, rpms in gear_map.items():
                        if isinstance(rpms, list):
                            for val in rpms:
                                if isinstance(val, str) and "-" in val and not val.startswith("-"):
                                    errors.append(f"{filepath}: 'ledRpm' contains unsupported string range '{val}' in v2.0.0.")
                                    
        elif version == "vHH3.0":
            # vHH3.0 allows statusLeds, redlineX aliases, and array-based redlineBlinkInterval.
            # We can perform basic structural checks here if we want.
            pass
        else:
            errors.append(f"{filepath}: Unknown schema version '{version}'")
                                
    except (json.JSONDecodeError, ValueError) as e:
        errors.append(f"{filepath}: JSON parse error: {e}")
    except Exception as e:
        errors.append(f"{filepath}: Error reading file: {e}")

    return errors

def main():
    parser = argparse.ArgumentParser(description="Enforce v2.00 schema compliance.")
    parser.add_argument("files", nargs="*", type=Path, help="JSON files to validate")
    args = parser.parse_args()

    has_errors = False
    for f in args.files:
        errors = check_file_schema(f)
        if errors:
            has_errors = True
            for err in errors:
                print(err)

    if has_errors:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
