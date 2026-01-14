# Manifest Generator

Generates `manifest.json` files for each sim data folder, making it easier for consuming applications to discover available cars without scanning directories.

## Usage

```bash
python3 scripts/generate_manifests.py
```

The script will:
- Scan all subdirectories in `data/`
- Read each car JSON file
- Extract `carName`, `carId`, and filename
- Generate a `manifest.json` in each sim folder
- Report any errors or invalid files

## Output Format

Each `manifest.json` contains:

```json
{
  "cars": [
    {
      "carName": "Ferrari 488 GT3",
      "carId": "ferrari_488_gt3",
      "path": "ferrari_488_gt3.json"
    }
  ]
}
```

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
- Report all errors but continue processing
- Only create manifest if at least one valid car exists
