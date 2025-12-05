"""Unit tests for prompt validators."""

import pytest
import os
import tempfile
from pathlib import Path

from lattice_lock_agents.prompt_architect.validators import (
    PromptValidator,
    ConventionChecker,
    QualityScorer,
    ValidationResult,
    ConventionResult,
    QualityScore,
)


# Sample valid prompt content
VALID_PROMPT = """# Prompt 1.1.1 - Package Infrastructure Setup

**Tool:** Devin AI
**Epic:** 1.1 - Package Model Orchestrator
**Phase:** 1 - Foundation

## Context

The Lattice Lock Framework has an existing Model Orchestrator at `src/lattice_lock_orchestrator/` with modules for core routing, scoring, registry, and API clients. This needs to be packaged as an importable Python library.

## Goal

Create the package infrastructure to make the Model Orchestrator installable as a Python package.

## Steps

1. Create `pyproject.toml` at the repo root with package configuration
2. Create `src/lattice_lock/__init__.py` with exports
3. Update `version.txt` format if needed
4. Create `tests/test_package_import.py` to verify imports
5. Test with `pip install -e .` and verify imports work
6. Run existing tests to ensure no regressions

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `pip install -e .` succeeds
- `from lattice_lock import ModelOrchestrator` works
- `from lattice_lock import __version__` returns `2.1.0`
- Existing tests still pass

## Notes

- Pre-existing broken tests are out of scope
- Use src-layout for package structure
"""

# Sample invalid prompt content (missing sections)
INVALID_PROMPT_MISSING_SECTIONS = """# Prompt 1.1.1 - Package Infrastructure

**Tool:** Devin AI
**Epic:** 1.1 - Package Model Orchestrator
**Phase:** 1 - Foundation

## Context

Some context here.

## Goal

Create something.
"""

# Sample prompt with poor quality
LOW_QUALITY_PROMPT = """# Prompt 1.1.1 - Do stuff

**Tool:** Devin AI
**Epic:** 1.1 - Epic
**Phase:** 1 - Phase

## Context

Context.

## Goal

Do stuff.

## Steps

1. Do thing
2. Do other thing

## Do NOT Touch

- stuff

## Success Criteria

- Done

## Notes

- None
"""


class TestPromptValidator:
    """Tests for PromptValidator class."""

    def test_validate_valid_prompt(self, tmp_path):
        """Test validation of a well-formed prompt."""
        prompt_file = tmp_path / "1.1.1_devin_test.md"
        prompt_file.write_text(VALID_PROMPT)

        validator = PromptValidator()
        result = validator.validate(str(prompt_file))

        assert result.is_valid
        assert not result.errors
        assert result.metadata.get("prompt_id") == "1.1.1"
        assert result.metadata.get("tool") == "Devin AI"

    def test_validate_missing_sections(self, tmp_path):
        """Test validation catches missing sections."""
        prompt_file = tmp_path / "1.1.1_devin_test.md"
        prompt_file.write_text(INVALID_PROMPT_MISSING_SECTIONS)

        validator = PromptValidator()
        result = validator.validate(str(prompt_file))

        assert not result.is_valid
        assert any("Steps" in e for e in result.errors)
        assert any("Do NOT Touch" in e for e in result.errors)
        assert any("Success Criteria" in e for e in result.errors)

    def test_validate_missing_header(self, tmp_path):
        """Test validation catches missing header."""
        prompt_file = tmp_path / "bad.md"
        prompt_file.write_text("Just some text without proper header")

        validator = PromptValidator()
        result = validator.validate(str(prompt_file))

        assert not result.is_valid
        assert any("header" in e.lower() for e in result.errors)

    def test_validate_missing_metadata(self, tmp_path):
        """Test validation catches missing metadata."""
        content = """# Prompt 1.1.1 - Test

Some content without metadata.

## Context

Context here.
"""
        prompt_file = tmp_path / "test.md"
        prompt_file.write_text(content)

        validator = PromptValidator()
        result = validator.validate(str(prompt_file))

        assert not result.is_valid
        assert any("Tool" in e for e in result.errors)
        assert any("Epic" in e for e in result.errors)
        assert any("Phase" in e for e in result.errors)

    def test_validate_content_directly(self):
        """Test validation of content without file."""
        validator = PromptValidator()
        result = validator.validate_content(VALID_PROMPT)

        assert result.is_valid
        assert result.metadata.get("prompt_id") == "1.1.1"

    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file."""
        validator = PromptValidator()
        result = validator.validate("/nonexistent/path/to/file.md")

        assert not result.is_valid
        assert any("not found" in e.lower() for e in result.errors)

    def test_section_validation_steps_count(self):
        """Test validation warns about step count."""
        content = """# Prompt 1.1.1 - Test

**Tool:** Devin AI
**Epic:** 1.1 - Epic
**Phase:** 1 - Phase

## Context

Context with `file.py` reference.

## Goal

Single goal.

## Steps

1. Step one
2. Step two

## Do NOT Touch

- `src/other/`

## Success Criteria

- Works correctly

## Notes

- Note here
"""
        validator = PromptValidator()
        result = validator.validate_content(content)

        # Should warn about too few steps
        steps_section = result.sections.get("Steps")
        assert steps_section is not None
        assert any("only 2 items" in w.lower() for w in steps_section.warnings)

    def test_strict_mode(self, tmp_path):
        """Test strict mode treats warnings as errors."""
        prompt_file = tmp_path / "test.md"
        prompt_file.write_text(LOW_QUALITY_PROMPT)

        # Normal mode: warnings don't fail validation
        validator = PromptValidator(strict_mode=False)
        result = validator.validate(str(prompt_file))
        # May have warnings but should be valid since required sections present

        # Strict mode: warnings cause failure
        strict_validator = PromptValidator(strict_mode=True)
        strict_result = strict_validator.validate(str(prompt_file))
        # If there are warnings, it should fail in strict mode
        if strict_result.warnings:
            assert not strict_result.is_valid


class TestConventionChecker:
    """Tests for ConventionChecker class."""

    def test_valid_filename(self):
        """Test valid filename format."""
        checker = ConventionChecker()
        result = checker.check_filename("1.1.1_devin_package_infrastructure.md")

        assert result.is_valid
        assert result.filename_valid
        assert result.extracted_info["phase"] == 1
        assert result.extracted_info["epic"] == 1
        assert result.extracted_info["task"] == 1
        assert result.extracted_info["tool"] == "devin"
        assert result.extracted_info["task_id"] == "1.1.1"

    def test_valid_filename_with_done_prefix(self):
        """Test filename with DONE- prefix."""
        checker = ConventionChecker()
        result = checker.check_filename("DONE-1.1.1_devin_package.md")

        assert result.is_valid
        assert result.extracted_info["has_done_prefix"]
        assert result.extracted_info["task_id"] == "1.1.1"

    def test_valid_filename_with_started_prefix(self):
        """Test filename with STARTED- prefix."""
        checker = ConventionChecker()
        result = checker.check_filename("STARTED-4.1.1_claude_docs_installation.md")

        assert result.is_valid
        assert result.extracted_info["has_started_prefix"]

    def test_invalid_filename_format(self):
        """Test invalid filename format."""
        checker = ConventionChecker()

        # Missing task ID
        result = checker.check_filename("devin_package.md")
        assert not result.is_valid
        assert not result.filename_valid

        # Wrong format
        result = checker.check_filename("1-1-1_devin_package.md")
        assert not result.is_valid

    def test_unknown_tool_warning(self):
        """Test warning for unknown tool identifier."""
        checker = ConventionChecker()
        result = checker.check_filename("1.1.1_unknown_tool_test.md")

        assert result.is_valid  # Still valid, just a warning
        assert any("not in known tools" in w for w in result.warnings)

    def test_placement_check(self, tmp_path):
        """Test directory placement validation."""
        # Create proper directory structure
        phase_dir = tmp_path / "project_prompts" / "phase1_foundation"
        phase_dir.mkdir(parents=True)

        prompt_file = phase_dir / "1.1.1_devin_test.md"
        prompt_file.write_text(VALID_PROMPT)

        checker = ConventionChecker(prompts_root=str(tmp_path / "project_prompts"))
        result = checker.check(str(prompt_file))

        assert result.placement_valid

    def test_placement_phase_mismatch(self, tmp_path):
        """Test detection of phase mismatch."""
        # Create wrong directory (phase2 for phase1 prompt)
        phase_dir = tmp_path / "project_prompts" / "phase2_cicd"
        phase_dir.mkdir(parents=True)

        prompt_file = phase_dir / "1.1.1_devin_test.md"
        prompt_file.write_text(VALID_PROMPT)

        checker = ConventionChecker(prompts_root=str(tmp_path / "project_prompts"))
        result = checker.check(str(prompt_file))

        assert not result.placement_valid
        assert any("doesn't match" in e for e in result.errors)

    def test_suggest_filename(self):
        """Test filename suggestion."""
        checker = ConventionChecker()
        suggested = checker.suggest_filename(
            phase=1,
            epic=2,
            task=3,
            tool="devin",
            description="Package Infrastructure Setup"
        )

        assert suggested == "1.2.3_devin_package_infrastructure_setup.md"

    def test_get_expected_directory(self):
        """Test expected directory mapping."""
        checker = ConventionChecker()

        assert checker.get_expected_directory(1) == "phase1_foundation"
        assert checker.get_expected_directory(2) == "phase2_cicd"
        assert checker.get_expected_directory(5) == "phase5_prompt_automation"
        assert checker.get_expected_directory(99) == "phase99_generic"


class TestQualityScorer:
    """Tests for QualityScorer class."""

    @pytest.mark.asyncio
    async def test_score_high_quality_prompt(self):
        """Test scoring of a high-quality prompt."""
        scorer = QualityScorer(threshold=6.0, use_llm=False)
        score = await scorer.score_content(VALID_PROMPT)

        assert score.overall_score >= 6.0
        assert score.passes_threshold
        assert not score.needs_review
        assert score.clarity_score > 5.0
        assert score.actionability_score > 5.0
        assert score.completeness_score > 5.0

    @pytest.mark.asyncio
    async def test_score_low_quality_prompt(self):
        """Test scoring of a low-quality prompt."""
        scorer = QualityScorer(threshold=6.0, use_llm=False)
        score = await scorer.score_content(LOW_QUALITY_PROMPT)

        # Low quality prompt should score lower
        assert score.clarity_score < 8.0
        assert len(score.feedback) > 0

    @pytest.mark.asyncio
    async def test_score_missing_sections(self):
        """Test scoring of prompt with missing sections."""
        scorer = QualityScorer(threshold=6.0, use_llm=False)
        score = await scorer.score_content(INVALID_PROMPT_MISSING_SECTIONS)

        assert score.completeness_score < 7.0
        assert not score.passes_threshold or score.overall_score < 6.0

    @pytest.mark.asyncio
    async def test_configurable_threshold(self):
        """Test configurable quality threshold."""
        low_threshold = QualityScorer(threshold=3.0, use_llm=False)
        high_threshold = QualityScorer(threshold=9.0, use_llm=False)

        low_score = await low_threshold.score_content(LOW_QUALITY_PROMPT)
        high_score = await high_threshold.score_content(LOW_QUALITY_PROMPT)

        # Same content, different thresholds
        assert low_score.overall_score == high_score.overall_score
        assert low_score.passes_threshold or not high_score.passes_threshold

    @pytest.mark.asyncio
    async def test_feedback_generation(self):
        """Test that feedback is generated for low scores."""
        scorer = QualityScorer(threshold=8.0, use_llm=False)
        score = await scorer.score_content(LOW_QUALITY_PROMPT)

        assert len(score.feedback) > 0
        assert len(score.suggestions) > 0

    @pytest.mark.asyncio
    async def test_score_file(self, tmp_path):
        """Test scoring from file."""
        prompt_file = tmp_path / "test.md"
        prompt_file.write_text(VALID_PROMPT)

        scorer = QualityScorer(use_llm=False)
        score = await scorer.score(str(prompt_file))

        assert score.prompt_path == str(prompt_file)
        assert score.overall_score > 0

    @pytest.mark.asyncio
    async def test_score_nonexistent_file(self):
        """Test scoring of nonexistent file."""
        scorer = QualityScorer(use_llm=False)
        score = await scorer.score("/nonexistent/file.md")

        assert score.needs_review
        assert any("not found" in f.lower() for f in score.feedback)


class TestValidationWithExistingPrompts:
    """Tests using existing prompts as ground truth."""

    @pytest.fixture
    def existing_prompts_dir(self):
        """Get the path to existing prompts directory."""
        # Try to find the project_prompts directory
        current_dir = Path(__file__).parent.parent
        prompts_dir = current_dir / "project_prompts"
        if prompts_dir.exists():
            return prompts_dir
        return None

    def test_existing_prompts_pass_validation(self, existing_prompts_dir):
        """Test that existing prompts pass validation."""
        if existing_prompts_dir is None:
            pytest.skip("project_prompts directory not found")

        validator = PromptValidator()
        checker = ConventionChecker()

        # Find all prompt files
        prompt_files = list(existing_prompts_dir.glob("**/*.md"))
        prompt_files = [
            p for p in prompt_files
            if not p.name.startswith("multi_agent")
            and not p.name.startswith("work_breakdown")
            and not p.name.startswith("project_prompts_tracker")
        ]

        if not prompt_files:
            pytest.skip("No prompt files found")

        failed_validations = []
        for prompt_file in prompt_files:
            result = validator.validate(str(prompt_file))
            if not result.is_valid:
                failed_validations.append((prompt_file.name, result.errors))

        # Assert all prompts pass validation
        assert len(failed_validations) == 0, (
            f"Failed validations: {failed_validations}"
        )

    def test_existing_prompts_follow_conventions(self, existing_prompts_dir):
        """Test that existing prompts follow naming conventions."""
        if existing_prompts_dir is None:
            pytest.skip("project_prompts directory not found")

        checker = ConventionChecker()

        # Find all prompt files (excluding non-prompt markdown files)
        prompt_files = list(existing_prompts_dir.glob("phase*/*.md"))

        if not prompt_files:
            pytest.skip("No prompt files found")

        failed_conventions = []
        for prompt_file in prompt_files:
            result = checker.check(str(prompt_file))
            if not result.filename_valid:
                failed_conventions.append((prompt_file.name, result.errors))

        # Assert all prompts follow conventions
        assert len(failed_conventions) == 0, (
            f"Failed conventions: {failed_conventions}"
        )


class TestValidatorIntegration:
    """Integration tests for validators working together."""

    @pytest.mark.asyncio
    async def test_full_validation_pipeline(self, tmp_path):
        """Test complete validation pipeline."""
        # Create a proper prompt file
        phase_dir = tmp_path / "project_prompts" / "phase1_foundation"
        phase_dir.mkdir(parents=True)
        prompt_file = phase_dir / "1.1.1_devin_test_feature.md"
        prompt_file.write_text(VALID_PROMPT)

        # Run all validators
        validator = PromptValidator()
        checker = ConventionChecker(prompts_root=str(tmp_path / "project_prompts"))
        scorer = QualityScorer(use_llm=False)

        validation_result = validator.validate(str(prompt_file))
        convention_result = checker.check(str(prompt_file))
        quality_score = await scorer.score(str(prompt_file))

        # All should pass for valid prompt
        assert validation_result.is_valid
        assert convention_result.is_valid
        assert quality_score.passes_threshold

    @pytest.mark.asyncio
    async def test_validation_result_serialization(self):
        """Test that validation results can be serialized."""
        validator = PromptValidator()
        result = validator.validate_content(VALID_PROMPT)

        # Should be serializable to dict
        result_dict = result.model_dump()
        assert isinstance(result_dict, dict)
        assert "is_valid" in result_dict
        assert "sections" in result_dict

        scorer = QualityScorer(use_llm=False)
        score = await scorer.score_content(VALID_PROMPT)

        score_dict = score.model_dump()
        assert isinstance(score_dict, dict)
        assert "overall_score" in score_dict
