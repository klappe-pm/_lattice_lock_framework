import sys
import tempfile
import unittest
from pathlib import Path

import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lattice_lock.orchestrator.registry import ModelRegistry
from lattice_lock.orchestrator.types import ModelProvider


class TestConfigurableRegistry(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.valid_yaml = Path(self.test_dir) / "models.yaml"
        self.invalid_yaml = Path(self.test_dir) / "invalid.yaml"

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir)

    def test_load_valid_yaml(self):
        data = {
            "version": "1.0",
            "models": [
                {
                    "id": "test-gpt",
                    "provider": "openai",
                    "context_window": 1000,
                    "input_cost": 1.0,
                    "output_cost": 2.0,
                    "reasoning_score": 80.0,
                    "coding_score": 90.0,
                }
            ],
        }
        with open(self.valid_yaml, "w") as f:
            yaml.dump(data, f)

        registry = ModelRegistry(registry_path=str(self.valid_yaml))

        self.assertIn("test-gpt", registry.models)
        model = registry.models["test-gpt"]
        self.assertEqual(model.provider, ModelProvider.OPENAI)
        self.assertEqual(model.coding_score, 90.0)

    def test_load_invalid_yaml(self):
        data = {
            "version": "1.0",
            "models": [
                {
                    "id": "bad-model",
                    # Missing provider and context_window
                }
            ],
        }
        with open(self.invalid_yaml, "w") as f:
            yaml.dump(data, f)

        # Should handle error gracefully and fall back or just load nothing
        registry = ModelRegistry(registry_path=str(self.invalid_yaml))
        # Depending on implementation, it might load valid models or fail completely.
        # Current impl fails method and falls back to defaults.
        # But here we didn't mock defaults yet.

        self.assertNotIn("bad-model", registry.models)

    def test_load_defaults_fallback(self):
        # Point to non-existent file
        registry = ModelRegistry(registry_path="/non/existent/path.yaml")
        # Should load defaults
        self.assertIn("gpt-4o", registry.models)
        self.assertIn("claude-3-5-sonnet", registry.models)

    def test_real_example_yaml(self):
        # Test against the actual example file we created
        project_root = Path(__file__).parent.parent
        example_path = project_root / "docs" / "examples" / "config" / "models.yaml"

        if not example_path.exists():
            self.skipTest("Example models.yaml not found")

        registry = ModelRegistry(registry_path=str(example_path))
        self.assertIn("gpt-4o", registry.models)
        self.assertIn("claude-3-5-sonnet", registry.models)
        self.assertIn("codellama:34b", registry.models)


if __name__ == "__main__":
    unittest.main()
