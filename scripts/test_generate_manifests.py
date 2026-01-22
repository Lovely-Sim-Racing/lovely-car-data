#!/usr/bin/env python3
"""Tests for generate_manifest.py"""

import json
import tempfile
import unittest
from pathlib import Path

import generate_manifest


class TestGenerateManifest(unittest.TestCase):
    """Test suite for single root manifest generation."""
    
    def setUp(self):
        """Create temporary test directory structure."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.data_dir.mkdir()
    
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
    
    def create_car_file(self, sim_name: str, filename: str, car_data: dict):
        """Helper to create a car JSON file."""
        sim_dir = self.data_dir / sim_name
        sim_dir.mkdir(exist_ok=True)
        car_file = sim_dir / filename
        with open(car_file, 'w', encoding='utf-8') as f:
            json.dump(car_data, f)
        return car_file
    
    def test_load_car_data_valid(self):
        """Test loading valid car data."""
        car_file = self.create_car_file("TestSim", "test_car.json", {
            "carName": "Test Car",
            "carId": "test_car",
            "ledNumber": 5
        })
        
        result = generate_manifest.load_car_data(car_file)
        
        self.assertEqual(result["carName"], "Test Car")
        self.assertEqual(result["carId"], "test_car")
        self.assertEqual(result["path"], "test_car.json")
    
    def test_load_car_data_missing_car_name(self):
        """Test loading car data with missing carName (should use empty string)."""
        car_file = self.create_car_file("TestSim", "test_car.json", {
            "carId": "test_car"
        })
        
        result = generate_manifest.load_car_data(car_file)
        
        self.assertEqual(result["carName"], "")
        self.assertEqual(result["carId"], "test_car")
    
    def test_load_car_data_missing_car_id(self):
        """Test loading car data with missing carId (should raise error)."""
        car_file = self.create_car_file("TestSim", "test_car.json", {
            "carName": "Test Car"
        })
        
        with self.assertRaises(ValueError):
            generate_manifest.load_car_data(car_file)
    
    def test_load_car_data_unicode(self):
        """Test loading car data with unicode characters."""
        car_file = self.create_car_file("TestSim", "test_car.json", {
            "carName": "Lamborghini Huracán EVO",
            "carId": "lamborghini_huracan_evo"
        })
        
        result = generate_manifest.load_car_data(car_file)
        
        self.assertEqual(result["carName"], "Lamborghini Huracán EVO")
    
    def test_generate_manifest_single_car(self):
        """Generate single root manifest with one car in one sim."""
        self.create_car_file("TestSim", "car1.json", {
            "carName": "Car 1",
            "carId": "car_1"
        })

        count = generate_manifest.generate_manifest(self.data_dir)

        self.assertEqual(count, 1)

        manifest_file = self.data_dir / "manifest.json"
        self.assertTrue(manifest_file.exists())

        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        self.assertIn("TestSim", manifest["cars"])
        self.assertEqual(len(manifest["cars"]["TestSim"]), 1)
        self.assertEqual(manifest["cars"]["TestSim"][0]["carName"], "Car 1")
        self.assertEqual(manifest["cars"]["TestSim"][0]["path"], "TestSim/car1.json")
    
    def test_generate_manifest_multiple_cars_across_sims(self):
        """Generate root manifest with multiple cars across sims and sorted."""
        self.create_car_file("TestSimA", "car2.json", {
            "carName": "Car 2",
            "carId": "car_2"
        })
        self.create_car_file("TestSimA", "car1.json", {
            "carName": "Car 1",
            "carId": "car_1"
        })
        self.create_car_file("TestSimB", "alpha.json", {
            "carName": "Alpha",
            "carId": "alpha"
        })

        count = generate_manifest.generate_manifest(self.data_dir)
        self.assertEqual(count, 3)

        with open(self.data_dir / "manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        cars = manifest["cars"]
        self.assertIn("TestSimA", cars)
        self.assertIn("TestSimB", cars)
        self.assertEqual([c["path"] for c in cars["TestSimA"]], ["TestSimA/car1.json", "TestSimA/car2.json"])
        self.assertEqual([c["path"] for c in cars["TestSimB"]], ["TestSimB/alpha.json"])
    
    def test_generate_manifest_sorted_order_within_sims(self):
        """Cars are sorted alphabetically by filename within each sim and sims are sorted."""
        self.create_car_file("SimZ", "zebra.json", {"carName": "Zebra", "carId": "zebra"})
        self.create_car_file("SimZ", "alpha.json", {"carName": "Alpha", "carId": "alpha"})
        self.create_car_file("SimA", "beta.json", {"carName": "Beta", "carId": "beta"})

        generate_manifest.generate_manifest(self.data_dir)

        with open(self.data_dir / "manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        cars = manifest["cars"]
        self.assertIn("SimA", cars)
        self.assertIn("SimZ", cars)
        self.assertEqual([c["path"] for c in cars["SimA"]], ["SimA/beta.json"]) 
        self.assertEqual([c["path"] for c in cars["SimZ"]], ["SimZ/alpha.json", "SimZ/zebra.json"]) 
    
    def test_generate_manifest_skips_invalid_files(self):
        """Invalid files are skipped and only valid cars are output."""
        self.create_car_file("TestSim", "valid.json", {"carName": "Valid", "carId": "valid"})
        self.create_car_file("TestSim", "invalid.json", {"carName": "Invalid"})

        count = generate_manifest.generate_manifest(self.data_dir)

        self.assertEqual(count, 1)

        with open(self.data_dir / "manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        self.assertIn("TestSim", manifest["cars"])
        self.assertEqual(len(manifest["cars"]["TestSim"]), 1)
        self.assertEqual(manifest["cars"]["TestSim"][0]["carId"], "valid")
    
    def test_generate_manifest_empty_data_dir(self):
        """No manifest is created when there are no cars across sims."""
        (self.data_dir / "EmptySim").mkdir()

        count = generate_manifest.generate_manifest(self.data_dir)

        self.assertEqual(count, 0)
        self.assertFalse((self.data_dir / "manifest.json").exists())
    
    def test_generate_manifest_ignores_existing_per_sim_manifest(self):
        """Existing per-sim manifest files are ignored during aggregation."""
        self.create_car_file("TestSim", "car1.json", {"carName": "Car 1", "carId": "car_1"})

        sim_dir = self.data_dir / "TestSim"
        with open(sim_dir / "manifest.json", 'w') as f:
            json.dump({"cars": []}, f)

        count = generate_manifest.generate_manifest(self.data_dir)
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
