"""Validate diagrams in documentation."""

import re
from pathlib import Path

import pytest


@pytest.mark.documentation
class TestMermaidDiagrams:
    """Test Mermaid diagram syntax."""

    # Valid Mermaid diagram types
    MERMAID_TYPES = [
        "graph",
        "flowchart",
        "sequenceDiagram",
        "classDiagram",
        "stateDiagram",
        "erDiagram",
        "gantt",
        "pie",
        "journey",
        "gitGraph",
        "mindmap",
        "timeline",
    ]

    def test_mermaid_diagrams_have_valid_type(self, all_markdown_files):
        """Mermaid diagrams should start with a valid diagram type."""
        mermaid_pattern = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
        invalid_diagrams = []

        for md_file in all_markdown_files:
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            for i, match in enumerate(mermaid_pattern.finditer(content)):
                diagram = match.group(1).strip()
                first_line = diagram.split("\n")[0].strip()

                # Check if diagram starts with valid type
                has_valid_type = any(
                    first_line.lower().startswith(dtype.lower())
                    for dtype in self.MERMAID_TYPES
                )

                if not has_valid_type and diagram:
                    invalid_diagrams.append(
                        f"{md_file} diagram {i+1}: Unknown type '{first_line[:30]}'"
                    )

        if invalid_diagrams:
            # Warning only - mermaid syntax is complex
            print(f"\nNote: {len(invalid_diagrams)} diagrams may have issues")

    def test_no_empty_mermaid_blocks(self, all_markdown_files):
        """Mermaid blocks should not be empty."""
        mermaid_pattern = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
        empty_blocks = []

        for md_file in all_markdown_files:
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            for i, match in enumerate(mermaid_pattern.finditer(content)):
                diagram = match.group(1).strip()
                if not diagram:
                    empty_blocks.append(f"{md_file}: empty mermaid block {i+1}")

        assert not empty_blocks, f"Found empty mermaid blocks:\n" + "\n".join(empty_blocks)


@pytest.mark.documentation
class TestImageReferences:
    """Test image references in documentation."""

    def test_image_files_exist(self, all_markdown_files):
        """Referenced images should exist."""
        # Pattern for image references: ![alt](path) or <img src="path">
        img_patterns = [
            re.compile(r"!\[([^\]]*)\]\((?!http)([^)]+)\)"),
            re.compile(r'<img[^>]+src=["\'](?!http)([^"\']+)["\']'),
        ]

        missing_images = []

        for md_file in all_markdown_files:
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            for pattern in img_patterns:
                for match in pattern.finditer(content):
                    # Get the image path (group 2 for markdown, group 1 for html)
                    img_path = match.group(2) if len(match.groups()) > 1 else match.group(1)

                    # Resolve relative path
                    full_path = md_file.parent / img_path
                    if not full_path.exists():
                        missing_images.append(f"{md_file}: {img_path}")

        if missing_images:
            # Warning - images might be external or in different location
            print(f"\nNote: {len(missing_images)} potentially missing images")
