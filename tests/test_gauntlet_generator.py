import pytest
import yaml
from pathlib import Path
from lattice_lock_gauntlet.generator import GauntletGenerator
from lattice_lock_gauntlet.parser import LatticeParser

@pytest.fixture
def sample_lattice_yaml(tmp_path):
    content = """
    version: "1.0"
    generated_module: "test_module"
    entities:
      TestEntity:
        fields:
          age:
            type: int
            gt: 0
            lt: 150
          score:
            type: decimal
            gte: 0.0
            lte: 100.0
          username:
            type: str
            unique: true
    """
    file_path = tmp_path / "lattice.yaml"
    file_path.write_text(content)
    return file_path

def test_parser_extracts_constraints(sample_lattice_yaml):
    parser = LatticeParser(str(sample_lattice_yaml))
    entities = parser.parse()
    
    assert len(entities) == 1
    entity = entities[0]
    assert entity.name == "TestEntity"
    
    # Check constraints
    constraints = {c.name: c for c in entity.ensures}
    assert "age_gt_0" in constraints
    assert "age_lt_150" in constraints
    assert "score_gte_0_0" in constraints
    assert "score_lte_100_0" in constraints
    assert "username_unique" in constraints
    
    assert constraints["age_gt_0"].value == 0
    assert constraints["age_gt_0"].constraint == "gt"

def test_generator_creates_files(sample_lattice_yaml, tmp_path):
    output_dir = tmp_path / "tests"
    generator = GauntletGenerator(str(sample_lattice_yaml), str(output_dir))
    generator.generate()
    
    expected_file = output_dir / "test_contract_TestEntity.py"
    assert expected_file.exists()
    
    content = expected_file.read_text()
    assert "class TestTestEntityContract:" in content
    assert "def test_age_gt_0" in content
    assert "assert value > 0" in content
    assert "def test_score_lte_100_0" in content
    assert "assert value <= 100.0" in content

def test_generated_code_is_valid_python(sample_lattice_yaml, tmp_path):
    output_dir = tmp_path / "tests"
    generator = GauntletGenerator(str(sample_lattice_yaml), str(output_dir))
    generator.generate()
    
    test_file = output_dir / "test_contract_TestEntity.py"
    
    # Compile the generated code to check for syntax errors
    compile(test_file.read_text(), str(test_file), "exec")
