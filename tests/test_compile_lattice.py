import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lattice_lock.compile import compile_lattice


class TestCompileLattice(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        PROJECT_ROOT = Path(__file__).parent.parent
        self.fixtures_dir = PROJECT_ROOT / "tests" / "fixtures"
        self.examples_dir = PROJECT_ROOT / "examples"

        self.valid_schema = self.examples_dir / "basic" / "lattice.yaml"
        self.invalid_schema = self.fixtures_dir / "invalid_lattice.yaml"

        # Ensure example exists (might be missing if sync failed)
        if not self.valid_schema.exists():
            self.skipTest("Examples not found")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_compile_valid_schema(self):
        output_dir = self.test_dir / "out"
        result = compile_lattice(
            schema_path=self.valid_schema,
            output_dir=output_dir,
            generate_pydantic=True,
            generate_gauntlet=True,
        )
        self.assertTrue(result.success)
        self.assertTrue((output_dir / "tests").exists())
        # Check for generated pydantic file (default name)
        pydantic_files = list(output_dir.glob("*_pydantic.py"))
        self.assertTrue(len(pydantic_files) > 0, "No pydantic files generated")

        # Check generated files list
        self.assertTrue(len(result.generated_files) > 0)

    def test_compile_invalid_schema(self):
        if not self.invalid_schema.exists():
            # Create dummy invalid file if missing
            self.fixtures_dir.mkdir(parents=True, exist_ok=True)
            with open(self.invalid_schema, "w") as f:
                f.write("invalid: yaml: content")

        result = compile_lattice(schema_path=self.invalid_schema, output_dir=self.test_dir / "out")
        self.assertFalse(result.success)
        self.assertTrue(len(result.errors) > 0)

    def test_compile_no_gauntlet(self):
        output_dir = self.test_dir / "out_no_gauntlet"
        result = compile_lattice(
            schema_path=self.valid_schema, output_dir=output_dir, generate_gauntlet=False
        )
        self.assertTrue(result.success)
        self.assertFalse((output_dir / "tests").exists())
        pydantic_files = list(output_dir.glob("*_pydantic.py"))
        self.assertTrue(len(pydantic_files) > 0, "No pydantic files generated")


if __name__ == "__main__":
    unittest.main()
