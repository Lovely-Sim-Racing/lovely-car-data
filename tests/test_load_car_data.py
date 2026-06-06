import pytest
import generate_manifest

def test_load_car_data_valid(temp_data_dir, create_car_file):
    """Test loading valid car data."""
    car_file = create_car_file(temp_data_dir, "TestSim", "test_car.json", {
        "carName": "Test Car",
        "carId": "test_car",
        "ledNumber": 5
    })
    
    result = generate_manifest.load_car_data(car_file)
    
    assert result["carName"] == "Test Car"
    assert result["carId"] == "test_car"
    assert result["path"] == "test_car.json"

def test_load_car_data_missing_car_name(temp_data_dir, create_car_file):
    """Test loading car data with missing carName (should use empty string)."""
    car_file = create_car_file(temp_data_dir, "TestSim", "test_car.json", {
        "carId": "test_car"
    })
    
    result = generate_manifest.load_car_data(car_file)
    
    assert result["carName"] == ""
    assert result["carId"] == "test_car"

def test_load_car_data_missing_car_id(temp_data_dir, create_car_file):
    """Test loading car data with missing carId (should raise error)."""
    car_file = create_car_file(temp_data_dir, "TestSim", "test_car.json", {
        "carName": "Test Car"
    })
    
    with pytest.raises(ValueError):
        generate_manifest.load_car_data(car_file)

def test_load_car_data_unicode(temp_data_dir, create_car_file):
    """Test loading car data with unicode characters."""
    car_file = create_car_file(temp_data_dir, "TestSim", "test_car.json", {
        "carName": "Lamborghini Huracán EVO",
        "carId": "lamborghini_huracan_evo"
    })
    
    result = generate_manifest.load_car_data(car_file)
    
    assert result["carName"] == "Lamborghini Huracán EVO"
