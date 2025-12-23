import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lattice_lock.validator.schema import validate_lattice_schema


class TestLatticeExamples(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).parent.parent
        self.examples_dir = self.root_dir / "docs" / "examples"
        self.fixtures_dir = self.root_dir / "tests" / "fixtures"

    def test_basic_example(self):
        path = str(self.examples_dir / "basic" / "lattice.yaml")
        if not Path(path).exists():
            self.skipTest("Basic example not found")
        result = validate_lattice_schema(path)
        self.assertTrue(result.valid, f"Basic example validation failed: {result.errors}")

    def test_advanced_example(self):
        path = str(self.examples_dir / "advanced" / "lattice.yaml")
        if not Path(path).exists():
            self.skipTest("Advanced example not found")
        result = validate_lattice_schema(path)
        self.assertTrue(result.valid, f"Advanced example validation failed: {result.errors}")

    def test_valid_fixture(self):
        path = str(self.fixtures_dir / "valid_lattice.yaml")
        if not Path(path).exists():
            self.skipTest("Valid fixture not found")
        result = validate_lattice_schema(path)
        self.assertTrue(result.valid, f"Valid fixture validation failed: {result.errors}")

    def test_invalid_fixture(self):
        path = str(self.fixtures_dir / "invalid_lattice.yaml")
        if not Path(path).exists():
            self.skipTest("Invalid fixture not found")
        result = validate_lattice_schema(path)
        self.assertFalse(result.valid, "Invalid fixture SHOULD have failed validation")


if __name__ == "__main__":
    unittest.main()
