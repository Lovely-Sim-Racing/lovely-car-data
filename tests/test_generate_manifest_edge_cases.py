import json
import generate_manifest

def test_generate_manifest_empty_data_dir(temp_data_dir):
    """No manifest is created when there are no cars across sims."""
    (temp_data_dir / "EmptySim").mkdir()

    count = generate_manifest.generate_manifest(temp_data_dir)

    assert count == 0
    assert not (temp_data_dir / "manifest.json").exists()

def test_generate_manifest_ignores_existing_per_sim_manifest(temp_data_dir, create_car_file):
    """Existing per-sim manifest files are ignored during aggregation."""
    create_car_file(temp_data_dir, "TestSim", "car1.json", {"carName": "Car 1", "carId": "car_1"})

    sim_dir = temp_data_dir / "TestSim"
    with open(sim_dir / "manifest.json", 'w') as f:
        json.dump({"cars": []}, f)

    count = generate_manifest.generate_manifest(temp_data_dir)
    assert count == 1
