# Manifest Generator

Generates a single `manifest.json` at `data/` containing all cars across supported sim game folders. This makes it easy for consuming applications to discover available cars globally and filter by game.

## Usage

```bash
python3 scripts/generate_manifest.py
```

The script will:
- Scan all subdirectories in `data/`
- Read each car JSON file (ignoring any existing per-sim `manifest.json` files)
- Extract `carName`, `carId`, and filename
- Generate a single `data/manifest.json` with entries including the game name
- Report any errors or invalid files per game folder

## Output Format

The root `data/manifest.json` contains:

```json
{
  "cars": {
    "AssettoCorsa": [
      {
        "carName": "Ferrari 488 GT3",
        "carId": "ferrari_488_gt3",
        "path": "AssettoCorsa/ferrari_488_gt3.json"
      }
    ],
    "AssettoCorsaCompetizione": [
      { "carName": "BMW M4 GT3", "carId": "bmw_m4_gt3", "path": "AssettoCorsaCompetizione/bmw_m4_gt3.json" }
    ]
  }
}
```

Notes:
- Top-level `cars` is an object keyed by game folder name.
- Each game contains an array of car entries.
- `path` is relative to `data/` and includes the game folder.

## Testing

Run the test suite:

```bash
python3 scripts/test_generate_manifests.py
```

For verbose output:

```bash
python3 scripts/test_generate_manifests.py -v
```

## Requirements

- Python 3.6+
- No external dependencies

## Error Handling

The script will:
- Skip files with invalid JSON
- Skip files missing required `carId` field
- Report all errors but continue processing, grouped per game folder
- Only create the root manifest if at least one valid car exists
