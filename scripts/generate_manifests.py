#!/usr/bin/env python3
"""Generate manifest.json files for each sim data folder."""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_car_data(car_file: Path) -> Dict[str, str]:
    """Load car data from JSON file and extract required fields."""
    with open(car_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    car_name = data.get("carName", "")
    car_id = data.get("carId", "")
    
    if not car_id:
        raise ValueError(f"Missing carId in {car_file}")
    
    return {
        "carName": car_name,
        "carId": car_id,
        "path": car_file.name
    }


def generate_manifest(sim_folder: Path) -> int:
    """Generate manifest.json for a sim folder. Returns number of cars."""
    cars: List[Dict[str, str]] = []
    errors: List[str] = []
    
    for car_file in sorted(sim_folder.glob("*.json")):
        if car_file.name == "manifest.json":
            continue
        
        try:
            cars.append(load_car_data(car_file))
        except (json.JSONDecodeError, ValueError) as e:
            errors.append(f"  {car_file.name}: {e}")
    
    if errors:
        print(f"⚠️  {sim_folder.name}: Skipped {len(errors)} file(s)")
        for error in errors:
            print(error)
    
    if not cars:
        return 0
    
    manifest = {"cars": cars}
    manifest_path = sim_folder / "manifest.json"
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    print(f"✓ {sim_folder.name}: {len(cars)} car(s)")
    return len(cars)


def main() -> int:
    """Main entry point."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    
    if not data_dir.exists():
        print(f"Error: data directory not found at {data_dir}", file=sys.stderr)
        return 1
    
    total_cars = 0
    total_sims = 0
    
    for sim_folder in sorted(data_dir.iterdir()):
        if not sim_folder.is_dir() or sim_folder.name.startswith('.'):
            continue
        
        car_count = generate_manifest(sim_folder)
        if car_count > 0:
            total_cars += car_count
            total_sims += 1
    
    print(f"\n✓ Generated {total_sims} manifest(s) with {total_cars} total car(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
