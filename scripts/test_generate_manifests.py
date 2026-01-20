#!/usr/bin/env python3
"""Tests for generate_manifests.py"""

import json
import tempfile
import unittest
from pathlib import Path

import generate_manifests


class TestGenerateManifests(unittest.TestCase):
    """Test suite for manifest generation."""
    
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
        
        result = generate_manifests.load_car_data(car_file)
        
        self.assertEqual(result["carName"], "Test Car")
        self.assertEqual(result["carId"], "test_car")
        self.assertEqual(result["path"], "test_car.json")
    
    def test_load_car_data_missing_car_name(self):
        """Test loading car data with missing carName (should use empty string)."""
        car_file = self.create_car_file("TestSim", "test_car.json", {
            "carId": "test_car"
        })
        
        result = generate_manifests.load_car_data(car_file)
        
        self.assertEqual(result["carName"], "")
        self.assertEqual(result["carId"], "test_car")
    
    def test_load_car_data_missing_car_id(self):
        """Test loading car data with missing carId (should raise error)."""
        car_file = self.create_car_file("TestSim", "test_car.json", {
            "carName": "Test Car"
        })
        
        with self.assertRaises(ValueError):
            generate_manifests.load_car_data(car_file)
    
    def test_load_car_data_unicode(self):
        """Test loading car data with unicode characters."""
        car_file = self.create_car_file("TestSim", "test_car.json", {
            "carName": "Lamborghini Huracán EVO",
            "carId": "lamborghini_huracan_evo"
        })
        
        result = generate_manifests.load_car_data(car_file)
        
        self.assertEqual(result["carName"], "Lamborghini Huracán EVO")
    
    def test_generate_manifest_single_car(self):
        """Test generating manifest with single car."""
        self.create_car_file("TestSim", "car1.json", {
            "carName": "Car 1",
            "carId": "car_1"
        })
        
        sim_dir = self.data_dir / "TestSim"
        count = generate_manifests.generate_manifest(sim_dir)
        
        self.assertEqual(count, 1)
        
        manifest_file = sim_dir / "manifest.json"
        self.assertTrue(manifest_file.exists())
        
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        self.assertEqual(len(manifest["cars"]), 1)
        self.assertEqual(manifest["cars"][0]["carName"], "Car 1")
    
    def test_generate_manifest_multiple_cars(self):
        """Test generating manifest with multiple cars."""
        self.create_car_file("TestSim", "car1.json", {
            "carName": "Car 1",
            "carId": "car_1"
        })
        self.create_car_file("TestSim", "car2.json", {
            "carName": "Car 2",
            "carId": "car_2"
        })
        
        sim_dir = self.data_dir / "TestSim"
        count = generate_manifests.generate_manifest(sim_dir)
        
        self.assertEqual(count, 2)
        
        with open(sim_dir / "manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        self.assertEqual(len(manifest["cars"]), 2)
        self.assertEqual(manifest["cars"][0]["carId"], "car_1")
        self.assertEqual(manifest["cars"][1]["carId"], "car_2")
    
    def test_generate_manifest_sorted_order(self):
        """Test that cars are sorted alphabetically by filename."""
        self.create_car_file("TestSim", "zebra.json", {
            "carName": "Zebra",
            "carId": "zebra"
        })
        self.create_car_file("TestSim", "alpha.json", {
            "carName": "Alpha",
            "carId": "alpha"
        })
        
        sim_dir = self.data_dir / "TestSim"
        generate_manifests.generate_manifest(sim_dir)
        
        with open(sim_dir / "manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        self.assertEqual(manifest["cars"][0]["carId"], "alpha")
        self.assertEqual(manifest["cars"][1]["carId"], "zebra")
    
    def test_generate_manifest_skips_invalid_files(self):
        """Test that invalid files are skipped with error reporting."""
        self.create_car_file("TestSim", "valid.json", {
            "carName": "Valid",
            "carId": "valid"
        })
        self.create_car_file("TestSim", "invalid.json", {
            "carName": "Invalid"
            # Missing carId
        })
        
        sim_dir = self.data_dir / "TestSim"
        count = generate_manifests.generate_manifest(sim_dir)
        
        self.assertEqual(count, 1)
        
        with open(sim_dir / "manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        self.assertEqual(len(manifest["cars"]), 1)
        self.assertEqual(manifest["cars"][0]["carId"], "valid")
    
    def test_generate_manifest_empty_folder(self):
        """Test generating manifest for empty folder."""
        sim_dir = self.data_dir / "EmptySim"
        sim_dir.mkdir()
        
        count = generate_manifests.generate_manifest(sim_dir)
        
        self.assertEqual(count, 0)
        self.assertFalse((sim_dir / "manifest.json").exists())
    
    def test_generate_manifest_ignores_existing_manifest(self):
        """Test that existing manifest.json is not processed as a car file."""
        self.create_car_file("TestSim", "car1.json", {
            "carName": "Car 1",
            "carId": "car_1"
        })
        
        # Create an existing manifest
        sim_dir = self.data_dir / "TestSim"
        with open(sim_dir / "manifest.json", 'w') as f:
            json.dump({"cars": []}, f)
        
        count = generate_manifests.generate_manifest(sim_dir)
        
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
