import json
import generate_manifest

def test_generate_manifest_multiple_cars_across_sims(temp_data_dir, create_car_file):
    """Generate root manifest with multiple cars across sims and sorted."""
    create_car_file(temp_data_dir, "TestSimA", "car2.json", {
        "carName": "Car 2",
        "carId": "car_2"
    })
    create_car_file(temp_data_dir, "TestSimA", "car1.json", {
        "carName": "Car 1",
        "carId": "car_1"
    })
    create_car_file(temp_data_dir, "TestSimB", "alpha.json", {
        "carName": "Alpha",
        "carId": "alpha"
    })

    count = generate_manifest.generate_manifest(temp_data_dir)
    assert count == 3

    with open(temp_data_dir / "manifest.json", 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    cars = manifest["cars"]
    assert "TestSimA" in cars
    assert "TestSimB" in cars
    assert [c["path"] for c in cars["TestSimA"]] == ["TestSimA/car1.json", "TestSimA/car2.json"]
    assert [c["path"] for c in cars["TestSimB"]] == ["TestSimB/alpha.json"]

def test_generate_manifest_sorted_order_within_sims(temp_data_dir, create_car_file):
    """Cars are sorted alphabetically by filename within each sim and sims are sorted."""
    create_car_file(temp_data_dir, "SimZ", "zebra.json", {"carName": "Zebra", "carId": "zebra"})
    create_car_file(temp_data_dir, "SimZ", "alpha.json", {"carName": "Alpha", "carId": "alpha"})
    create_car_file(temp_data_dir, "SimA", "beta.json", {"carName": "Beta", "carId": "beta"})

    generate_manifest.generate_manifest(temp_data_dir)

    with open(temp_data_dir / "manifest.json", 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    cars = manifest["cars"]
    assert "SimA" in cars
    assert "SimZ" in cars
    assert [c["path"] for c in cars["SimA"]] == ["SimA/beta.json"]
    assert [c["path"] for c in cars["SimZ"]] == ["SimZ/alpha.json", "SimZ/zebra.json"]
