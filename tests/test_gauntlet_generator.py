import pytest
import os
from pathlib import Path
from lattice_lock_gauntlet.generator import GauntletGenerator
from lattice_lock_gauntlet.parser import LatticeParser, EntityDefinition, EnsuresClause

TEST_LATTICE_YAML = """
entities:
  User:
    fields:
      age:
        gt: 18
        lt: 100
      score:
        gte: 0
        lte: 10
      username:
        unique: true
    ensures:
      - name: username_check
        field: username
        constraint: unique
        value: true
        description: "Username must be unique"
"""

@pytest.fixture
def lattice_file(tmp_path):
    f = tmp_path / "lattice.yaml"
    f.write_text(TEST_LATTICE_YAML)
    return str(f)

@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / "output"

def test_parser_parsing(lattice_file):
    parser = LatticeParser(lattice_file)
    entities = parser.parse()
    assert len(entities) == 1
    user = entities[0]
    assert user.name == "User"
    # 4 implicit (gt, lt, gte, lte, unique -> 5?)
    # age: gt, lt (2)
    # score: gte, lte (2)
    # username: unique (1)
    # explicit: 1
    # Total: 6
    assert len(user.ensures) == 6

def test_generator_creates_files(lattice_file, output_dir):
    generator = GauntletGenerator(lattice_file, str(output_dir))
    generator.generate()

    expected_file = output_dir / "test_contract_User.py"
    assert expected_file.exists()

    content = expected_file.read_text()
    assert "class TestUserContract:" in content
    assert "def test_age_gt_18" in content
    assert "def test_age_lt_100" in content
    assert "def test_score_gte_0" in content
    assert "def test_score_lte_10" in content
    assert "def test_username_unique" in content
    assert "def test_username_check" in content

    # Check fixture generation
    assert '"age": 19' in content  # gt 18 -> 19
    assert '"score": 0' in content # gte 0 -> 0

def test_generated_code_is_valid_python(lattice_file, output_dir):
    generator = GauntletGenerator(lattice_file, str(output_dir))
    generator.generate()

    expected_file = output_dir / "test_contract_User.py"

    # Compile checking
    import ast
    ast.parse(expected_file.read_text())

def test_generated_test_execution(lattice_file, output_dir):
    # This is a bit meta: we run pytest on the generated file
    generator = GauntletGenerator(lattice_file, str(output_dir))
    generator.generate()

    # We need to run pytest on this file.
    # The generated test uses a fixture that returns a dict.
    # The default fixture values should pass the tests.
    # age > 18 (19) -> Pass
    # age < 100 (19) -> Pass
    # score >= 0 (0) -> Pass
    # score <= 10 (0) -> Pass
    # unique -> Placeholder (Pass/Skip)
    # unique -> Placeholder (Pass/Skip)

    import pytest
    ret = pytest.main([str(output_dir)])
    assert ret == 0
