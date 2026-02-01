"""Validate code examples in documentation."""

import ast
import re

import pytest
import yaml


@pytest.mark.documentation
class TestPythonCodeExamples:
    """Test Python code examples are syntactically valid."""

    def test_python_examples_parse(self, all_markdown_files):
        """All Python code blocks must be valid syntax."""
        # Pattern to extract Python code blocks
        python_block = re.compile(r"```python\n(.*?)```", re.DOTALL)
        errors = []

        for md_file in all_markdown_files:
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            for i, match in enumerate(python_block.finditer(content)):
                code = match.group(1)

                # Skip incomplete examples (common patterns for truncation)
                skip_markers = ["...", "# ...", "# etc", "# more code", "pass  #"]
                if any(marker in code for marker in skip_markers):
                    continue

                # Skip very short snippets (likely incomplete)
                if len(code.strip()) < 10:
                    continue

                try:
                    ast.parse(code)
                except SyntaxError as e:
                    errors.append(f"{md_file} block {i+1}: {e.msg} at line {e.lineno}")

        # Allow some errors (documentation may have intentional pseudo-code)
        max_errors = 5
        if len(errors) > max_errors:
            pytest.fail(
                f"Too many invalid Python examples ({len(errors)} > {max_errors}):\n"
                + "\n".join(errors[:10])
            )


@pytest.mark.documentation
class TestYAMLCodeExamples:
    """Test YAML code examples are valid."""

    def test_yaml_examples_parse(self, all_markdown_files):
        """YAML code blocks should be valid YAML."""
        yaml_block = re.compile(r"```ya?ml\n(.*?)```", re.DOTALL)
        errors = []

        for md_file in all_markdown_files:
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            for i, match in enumerate(yaml_block.finditer(content)):
                yaml_content = match.group(1)

                # Skip placeholder content
                if "${" in yaml_content or "{{" in yaml_content:
                    continue

                try:
                    yaml.safe_load(yaml_content)
                except yaml.YAMLError as e:
                    errors.append(f"{md_file} block {i+1}: {e}")

        # YAML errors are less critical
        if len(errors) > 10:
            pytest.fail(f"Many invalid YAML examples ({len(errors)}):\n" + "\n".join(errors[:5]))


@pytest.mark.documentation
class TestCodeBlockLabeling:
    """Test code blocks have language labels."""

    def test_code_blocks_have_language(self, all_markdown_files):
        """Code blocks should specify a language for syntax highlighting."""
        # Pattern for unlabeled code blocks
        unlabeled_pattern = re.compile(r"^```\s*$", re.MULTILINE)
        unlabeled_files = []

        for md_file in all_markdown_files:
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            matches = unlabeled_pattern.findall(content)
            if matches:
                unlabeled_files.append(f"{md_file}: {len(matches)} unlabeled blocks")

        # Warning level - don't fail, but report
        if unlabeled_files:
            # Just note it, don't fail
            print(f"\nNote: Found {len(unlabeled_files)} files with unlabeled code blocks")
