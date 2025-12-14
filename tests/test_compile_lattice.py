"""Tests for the compile_lattice function and CLI.

This module validates that:
1. compile_lattice function works correctly with valid schemas
2. Error handling works for invalid schemas
3. Each generation option (pydantic, sqlmodel, gauntlet) works correctly
4. Output files are created in the correct locations
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path

from lattice_lock.compile import compile_lattice, CompilationResult


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestCompileLatticeFunction:
    """Tests for the compile_lattice function."""

    @pytest.fixture
    def basic_schema_path(self):
        return str(PROJECT_ROOT / "examples" / "basic" / "lattice.yaml")

    @pytest.fixture
    def advanced_schema_path(self):
        return str(PROJECT_ROOT / "examples" / "advanced" / "lattice.yaml")

    @pytest.fixture
    def invalid_schema_path(self):
        return str(PROJECT_ROOT / "tests" / "fixtures" / "invalid_lattice.yaml")

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_compile_basic_schema_success(self, basic_schema_path, temp_output_dir):
        """Test that compiling a basic schema succeeds."""
        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=temp_output_dir,
            generate_pydantic=True,
            generate_gauntlet=True,
        )

        assert result.success, f"Compilation should succeed. Errors: {result.errors}"
        assert len(result.errors) == 0, "Should have no errors"

    def test_compile_advanced_schema_success(self, advanced_schema_path, temp_output_dir):
        """Test that compiling an advanced schema succeeds."""
        result = compile_lattice(
            schema_path=advanced_schema_path,
            output_dir=temp_output_dir,
            generate_pydantic=True,
            generate_gauntlet=True,
        )

        assert result.success, f"Compilation should succeed. Errors: {result.errors}"
        assert len(result.errors) == 0, "Should have no errors"

    def test_compile_invalid_schema_fails(self, invalid_schema_path, temp_output_dir):
        """Test that compiling an invalid schema fails with appropriate errors."""
        result = compile_lattice(
            schema_path=invalid_schema_path,
            output_dir=temp_output_dir,
        )

        assert not result.success, "Compilation should fail for invalid schema"
        assert len(result.errors) > 0, "Should have errors"

    def test_compile_nonexistent_file_fails(self, temp_output_dir):
        """Test that compiling a nonexistent file fails."""
        result = compile_lattice(
            schema_path="nonexistent_file.yaml",
            output_dir=temp_output_dir,
        )

        assert not result.success, "Compilation should fail for nonexistent file"
        assert any("not found" in e.lower() for e in result.errors), "Should report file not found"

    def test_generates_pydantic_models(self, basic_schema_path, temp_output_dir):
        """Test that Pydantic models are generated when requested."""
        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=temp_output_dir,
            generate_pydantic=True,
            generate_gauntlet=False,
        )

        assert result.success, f"Compilation should succeed. Errors: {result.errors}"

        # Check that Pydantic file was generated
        pydantic_files = [f for f in result.generated_files if f.file_type == 'pydantic']
        assert len(pydantic_files) == 1, "Should generate one Pydantic file"
        assert pydantic_files[0].path.exists(), "Pydantic file should exist"

    def test_generates_sqlmodel_classes(self, basic_schema_path, temp_output_dir):
        """Test that SQLModel classes are generated when requested."""
        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=temp_output_dir,
            generate_pydantic=False,
            generate_sqlmodel=True,
            generate_gauntlet=False,
        )

        assert result.success, f"Compilation should succeed. Errors: {result.errors}"

        # Check that SQLModel file was generated
        sqlmodel_files = [f for f in result.generated_files if f.file_type == 'sqlmodel']
        assert len(sqlmodel_files) == 1, "Should generate one SQLModel file"
        assert sqlmodel_files[0].path.exists(), "SQLModel file should exist"

    def test_generates_gauntlet_tests(self, basic_schema_path, temp_output_dir):
        """Test that Gauntlet tests are generated when requested."""
        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=temp_output_dir,
            generate_pydantic=False,
            generate_gauntlet=True,
        )

        assert result.success, f"Compilation should succeed. Errors: {result.errors}"

        # Check that Gauntlet files were generated
        gauntlet_files = [f for f in result.generated_files if f.file_type == 'gauntlet']
        assert len(gauntlet_files) >= 1, "Should generate at least one Gauntlet test file"
        for f in gauntlet_files:
            assert f.path.exists(), f"Gauntlet file should exist: {f.path}"

    def test_no_generation_when_disabled(self, basic_schema_path, temp_output_dir):
        """Test that no files are generated when all options are disabled."""
        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=temp_output_dir,
            generate_pydantic=False,
            generate_sqlmodel=False,
            generate_gauntlet=False,
        )

        assert result.success, f"Compilation should succeed. Errors: {result.errors}"
        assert len(result.generated_files) == 0, "Should generate no files when all options disabled"

    def test_output_dir_created_if_not_exists(self, basic_schema_path, temp_output_dir):
        """Test that output directory is created if it doesn't exist."""
        new_output_dir = Path(temp_output_dir) / "new_subdir"
        assert not new_output_dir.exists(), "Output dir should not exist initially"

        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=str(new_output_dir),
            generate_pydantic=True,
            generate_gauntlet=False,
        )

        assert result.success, f"Compilation should succeed. Errors: {result.errors}"
        assert new_output_dir.exists(), "Output directory should be created"

    def test_compilation_result_has_validation_result(self, basic_schema_path, temp_output_dir):
        """Test that CompilationResult includes validation result."""
        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=temp_output_dir,
        )

        assert result.validation_result is not None, "Should include validation result"
        assert result.validation_result.valid, "Validation should pass for valid schema"


class TestCompilationResult:
    """Tests for the CompilationResult dataclass."""

    def test_add_error_marks_failure(self):
        """Test that adding an error marks the result as failed."""
        result = CompilationResult()
        assert result.success, "Should start as successful"

        result.add_error("Test error")

        assert not result.success, "Should be marked as failed after adding error"
        assert "Test error" in result.errors, "Error should be in errors list"

    def test_add_warning_does_not_mark_failure(self):
        """Test that adding a warning does not mark the result as failed."""
        result = CompilationResult()

        result.add_warning("Test warning")

        assert result.success, "Should still be successful after adding warning"
        assert "Test warning" in result.warnings, "Warning should be in warnings list"


class TestGeneratedPydanticModels:
    """Tests for the generated Pydantic models."""

    @pytest.fixture
    def basic_schema_path(self):
        return str(PROJECT_ROOT / "examples" / "basic" / "lattice.yaml")

    @pytest.fixture
    def generated_pydantic_file(self, basic_schema_path):
        """Generate Pydantic models and return the file path."""
        temp_dir = tempfile.mkdtemp()
        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=temp_dir,
            generate_pydantic=True,
            generate_gauntlet=False,
        )

        pydantic_files = [f for f in result.generated_files if f.file_type == 'pydantic']
        yield pydantic_files[0].path
        shutil.rmtree(temp_dir)

    def test_generated_pydantic_is_valid_python(self, generated_pydantic_file):
        """Test that generated Pydantic code is valid Python."""
        import ast
        content = generated_pydantic_file.read_text()
        ast.parse(content)  # Will raise SyntaxError if invalid

    def test_generated_pydantic_contains_entities(self, generated_pydantic_file):
        """Test that generated Pydantic code contains expected entities."""
        content = generated_pydantic_file.read_text()
        assert "class User(BaseModel):" in content, "Should contain User class"
        assert "class Product(BaseModel):" in content, "Should contain Product class"


class TestGeneratedGauntletTests:
    """Tests for the generated Gauntlet tests."""

    @pytest.fixture
    def basic_schema_path(self):
        return str(PROJECT_ROOT / "examples" / "basic" / "lattice.yaml")

    @pytest.fixture
    def generated_gauntlet_dir(self, basic_schema_path):
        """Generate Gauntlet tests and return the directory path."""
        temp_dir = tempfile.mkdtemp()
        result = compile_lattice(
            schema_path=basic_schema_path,
            output_dir=temp_dir,
            generate_pydantic=False,
            generate_gauntlet=True,
        )

        yield Path(temp_dir) / "tests"
        shutil.rmtree(temp_dir)

    def test_generated_gauntlet_files_exist(self, generated_gauntlet_dir):
        """Test that Gauntlet test files are created."""
        assert generated_gauntlet_dir.exists(), "Tests directory should exist"
        test_files = list(generated_gauntlet_dir.glob("test_contract_*.py"))
        assert len(test_files) >= 1, "Should have at least one test contract file"

    def test_generated_gauntlet_is_valid_python(self, generated_gauntlet_dir):
        """Test that generated Gauntlet tests are valid Python."""
        import ast
        for test_file in generated_gauntlet_dir.glob("test_contract_*.py"):
            content = test_file.read_text()
            ast.parse(content)  # Will raise SyntaxError if invalid
