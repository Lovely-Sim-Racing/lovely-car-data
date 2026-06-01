import json
import sys
from pathlib import Path
import pytest

# Add scripts directory to path to import generate_manifest
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary test directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def create_car_file():
    def _create_car_file(data_dir: Path, sim_name: str, filename: str, car_data: dict):
        """Helper to create a car JSON file."""
        sim_dir = data_dir / sim_name
        sim_dir.mkdir(exist_ok=True)
        car_file = sim_dir / filename
        with open(car_file, 'w', encoding='utf-8') as f:
            json.dump(car_data, f)
        return car_file
    return _create_car_file
