import json
import generate_manifest

def test_generate_manifest_skips_invalid_files(temp_data_dir, create_car_file):
    """Invalid files are skipped and only valid cars are output."""
    create_car_file(temp_data_dir, "TestSim", "valid.json", {"carName": "Valid", "carId": "valid"})
    create_car_file(temp_data_dir, "TestSim", "invalid.json", {"carName": "Invalid"})

    count = generate_manifest.generate_manifest(temp_data_dir)

    assert count == 1

    with open(temp_data_dir / "manifest.json", 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    assert "TestSim" in manifest["cars"]
    assert len(manifest["cars"]["TestSim"]) == 1
    assert manifest["cars"]["TestSim"][0]["carId"] == "valid"
