import json
import generate_manifest

def test_generate_manifest_single_car(temp_data_dir, create_car_file):
    """Generate single root manifest with one car in one sim."""
    create_car_file(temp_data_dir, "TestSim", "car1.json", {
        "carName": "Car 1",
        "carId": "car_1"
    })

    count = generate_manifest.generate_manifest(temp_data_dir)

    assert count == 1

    manifest_file = temp_data_dir / "manifest.json"
    assert manifest_file.exists()

    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    assert "TestSim" in manifest["cars"]
    assert len(manifest["cars"]["TestSim"]) == 1
    assert manifest["cars"]["TestSim"][0]["carName"] == "Car 1"
    assert manifest["cars"]["TestSim"][0]["path"] == "TestSim/car1.json"
