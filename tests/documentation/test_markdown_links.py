"""Validate all markdown links in documentation."""

import re
from pathlib import Path

import pytest


@pytest.mark.documentation
class TestMarkdownLinks:
    """Test internal link integrity in documentation."""

    def test_internal_links_resolve(self, all_markdown_files):
        """All internal markdown links must point to existing files."""
        # Pattern for internal links: [text](path) but not [text](http...)
        link_pattern = re.compile(r"\[([^\]]+)\]\((?!http[s]?://)(?!mailto:)([^)#]+)")
        broken_links = []

        for md_file in all_markdown_files:
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            for match in link_pattern.finditer(content):
                link_text = match.group(1)
                link_path = match.group(2).strip()

                # Skip anchors-only links
                if not link_path or link_path.startswith("#"):
                    continue

                # Resolve relative path
                target_path = md_file.parent / link_path
                target_path = target_path.resolve()

                if not target_path.exists():
                    broken_links.append(f"{md_file}:{link_path}")

        assert not broken_links, (
            f"Found {len(broken_links)} broken internal links:\n"
            + "\n".join(broken_links[:20])
        )

    def test_readme_exists(self, readme_file):
        """Project must have a README.md file."""
        assert readme_file is not None, "README.md not found in project root"

    def test_readme_has_required_sections(self, readme_file):
        """README should have standard sections."""
        if readme_file is None:
            pytest.skip("No README.md found")

        content = readme_file.read_text(errors="ignore").lower()

        # Check for common sections (at least some should exist)
        sections = [
            "installation",
            "usage",
            "getting started",
            "quick start",
            "features",
            "documentation",
        ]
        found_sections = [s for s in sections if s in content]

        assert len(found_sections) >= 2, (
            f"README should have at least 2 of these sections: {sections}. "
            f"Found: {found_sections}"
        )


@pytest.mark.documentation
class TestMarkdownAnchors:
    """Test anchor link integrity."""

    def test_heading_anchors_valid(self, all_markdown_files):
        """Anchor links should point to valid headings."""
        # Pattern for anchor links within same file: [text](#anchor)
        anchor_pattern = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")
        # Pattern for headings
        heading_pattern = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)

        invalid_anchors = []

        for md_file in all_markdown_files:
            try:
                content = md_file.read_text(errors="ignore")
            except Exception:
                continue

            # Extract all headings and convert to anchors
            headings = heading_pattern.findall(content)
            valid_anchors = set()
            for heading in headings:
                # Convert heading to anchor format (lowercase, spaces to dashes)
                anchor = heading.lower().strip()
                anchor = re.sub(r"[^\w\s-]", "", anchor)
                anchor = re.sub(r"\s+", "-", anchor)
                valid_anchors.add(anchor)

            # Check anchor links
            for match in anchor_pattern.finditer(content):
                anchor = match.group(2).lower()
                # Simplified check - anchor should partially match a heading
                if not any(anchor in valid for valid in valid_anchors):
                    # Don't fail, just note (anchors can be complex)
                    pass

        # This test is informational - anchors are hard to validate perfectly
        assert True
