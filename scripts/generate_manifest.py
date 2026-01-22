#!/usr/bin/env python3
"""Generate a single manifest.json at data/ containing all cars across sims.

Each car entry includes the source game folder name to enable filtering.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_car_data(car_file: Path) -> Dict[str, str]:
    """Load car data from JSON file and extract required fields.

    Returns minimal fields; game and full relative path are added by the generator.
    """
    with open(car_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    car_name = data.get("carName", "")
    car_id = data.get("carId", "")
    
    if not car_id:
        raise ValueError(f"Missing carId in {car_file}")
    
    return {
        "carName": car_name,
        "carId": car_id,
        "path": car_file.name,
    }


def generate_manifest(data_dir: Path) -> int:
    """Generate a single manifest.json in data_dir covering all sim folders.
    
    Structure:
    {
      "cars": {
        "AssettoCorsa": [ { "carName", "carId", "path" }, ... ],
        "AssettoCorsaCompetizione": [ ... ],
        ...
      }
    }
    
    Returns the total number of cars included. If no valid cars are found, no
    manifest file is created and 0 is returned.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    cars_by_game: Dict[str, List[Dict[str, str]]] = {}
    errors_by_sim: Dict[str, List[str]] = {}

    # Iterate deterministic: sort sim folders then files within
    for sim_folder in sorted([p for p in data_dir.iterdir() if p.is_dir() and not p.name.startswith('.')], key=lambda p: p.name):
        sim_errors: List[str] = []
        sim_cars: List[Dict[str, str]] = []
        for car_file in sorted(sim_folder.glob("*.json"), key=lambda p: p.name):
            if car_file.name == "manifest.json":
                # Ignore any existing per-sim manifests
                continue
            try:
                base = load_car_data(car_file)
                sim_cars.append({
                    "carName": base["carName"],
                    "carId": base["carId"],
                    "path": f"{sim_folder.name}/{base['path']}",
                })
            except (json.JSONDecodeError, ValueError) as e:
                sim_errors.append(f"  {car_file.name}: {e}")
        if sim_errors:
            errors_by_sim[sim_folder.name] = sim_errors
        if sim_cars:
            cars_by_game[sim_folder.name] = sim_cars

    # Print errors grouped by sim for visibility
    for sim_name, errs in errors_by_sim.items():
        print(f"⚠️  {sim_name}: Skipped {len(errs)} file(s)")
        for error in errs:
            print(error)

    total = sum(len(v) for v in cars_by_game.values())
    if total == 0:
        return 0

    manifest = {"cars": cars_by_game}
    manifest_path = data_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"✓ Generated manifest with {total} total car(s) across sims")
    return total


def main() -> int:
    """Main entry point."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    try:
        count = generate_manifest(data_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # No cars found is not considered an error for CLI purposes
    return 0


if __name__ == "__main__":
    sys.exit(main())
