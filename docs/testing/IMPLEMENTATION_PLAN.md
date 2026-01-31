# Testing Program Implementation Plan

**Status**: Phase 0 Complete (Definitions)
**Next**: Phase 1 (Core Infrastructure)

---

## Current State Assessment

### What Exists (Phase 0 - Complete)
- [x] Testing Program Plan document
- [x] Approver Agent YAML definition
- [x] Bug Automation Agent YAML definition
- [x] Agent Settings YAML configuration
- [x] pyproject.toml coverage configuration (90% target)
- [x] Test markers defined

### What's Missing (Critical Path)
- [ ] Python implementation for Approver Agent
- [ ] Settings loader and configuration management
- [ ] Actual test files for documentation validation
- [ ] Actual test files for code quality validation
- [ ] CI/CD workflow files (not just templates)
- [ ] Pre-commit hook integration
- [ ] GitHub Actions for agent execution

---

## Implementation Phases

### Phase 1: Core Infrastructure (Priority: Critical)

#### 1.1 Settings Loader
```
src/lattice_lock/agents/settings.py
```
- Load agent_settings.yaml
- Environment variable override support
- Runtime toggle for approver_agent.enabled
- Validation against schema

#### 1.2 Agent Base Implementation
```
src/lattice_lock/agents/base_agent.py
src/lattice_lock/agents/approver/
├── __init__.py
├── agent.py              # Main ApproverAgent class
├── coverage_analyzer.py  # CoverageAnalyst implementation
├── doc_validator.py      # DocumentationValidator implementation
├── index_manager.py      # IndexManager implementation
├── test_reviewer.py      # TestReviewer implementation
└── models.py             # Pydantic models for agent outputs
```

#### 1.3 Test Files for Documentation Validation
```
tests/documentation/
├── __init__.py
├── conftest.py
├── test_markdown_links.py      # Validate all internal links
├── test_code_examples.py       # Verify Python examples parse
├── test_diagram_syntax.py      # Validate Mermaid diagrams
└── test_style_compliance.py    # Check markdown style
```

#### 1.4 Test Files for Code Quality
```
tests/quality/
├── __init__.py
├── conftest.py
├── test_linting.py       # Programmatic ruff/black checks
├── test_type_hints.py    # MyPy validation tests
└── test_coverage.py      # Coverage threshold validation
```

---

### Phase 2: Agent Execution (Priority: High)

#### 2.1 Approver Agent Python Implementation

```python
# src/lattice_lock/agents/approver/agent.py

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml

from lattice_lock.agents.settings import AgentSettings, get_settings
from lattice_lock.agents.approver.coverage_analyzer import CoverageAnalyzer
from lattice_lock.agents.approver.doc_validator import DocumentationValidator
from lattice_lock.agents.approver.test_reviewer import TestReviewer


@dataclass
class ApprovalResult:
    approved: bool
    coverage_passed: bool
    docs_passed: bool
    tests_passed: bool
    blocking_issues: list[str]
    recommendations: list[str]


class ApproverAgent:
    """The single authority for testing and quality approvals."""

    def __init__(self, settings: Optional[AgentSettings] = None):
        self.settings = settings or get_settings()
        self._validate_enabled()

        # Initialize sub-agents
        self.coverage_analyzer = CoverageAnalyzer(self.settings)
        self.doc_validator = DocumentationValidator(self.settings)
        self.test_reviewer = TestReviewer(self.settings)

    def _validate_enabled(self) -> None:
        if not self.settings.agents.approver_agent.enabled:
            raise RuntimeError("ApproverAgent is disabled in settings")

    async def review_pr(self, pr_number: int) -> ApprovalResult:
        """Review a pull request for approval."""
        blocking_issues = []
        recommendations = []

        # Run coverage analysis
        coverage_result = await self.coverage_analyzer.analyze()
        if not coverage_result.meets_threshold:
            blocking_issues.append(
                f"Coverage {coverage_result.percentage}% below "
                f"{self.settings.agents.approver_agent.coverage.target}%"
            )

        # Run documentation validation
        doc_result = await self.doc_validator.validate()
        if doc_result.broken_links:
            blocking_issues.extend(
                f"Broken link: {link}" for link in doc_result.broken_links
            )

        # Run test review
        test_result = await self.test_reviewer.review_changed_tests()
        if test_result.quality_score < 70:
            blocking_issues.append(
                f"Test quality score {test_result.quality_score} below 70"
            )
        recommendations.extend(test_result.recommendations)

        return ApprovalResult(
            approved=len(blocking_issues) == 0,
            coverage_passed=coverage_result.meets_threshold,
            docs_passed=len(doc_result.broken_links) == 0,
            tests_passed=test_result.quality_score >= 70,
            blocking_issues=blocking_issues,
            recommendations=recommendations,
        )

    def is_enabled(self) -> bool:
        """Check if approver agent is enabled."""
        return self.settings.agents.approver_agent.enabled
```

#### 2.2 Settings Loader Implementation

```python
# src/lattice_lock/agents/settings.py

from pathlib import Path
from typing import Optional
import os
import yaml
from pydantic import BaseModel, Field


class CoverageSettings(BaseModel):
    enabled: bool = True
    target: int = 90
    warning_threshold: int = 85
    critical_threshold: int = 80
    enforcement_mode: str = "strict"


class ApproverAgentSettings(BaseModel):
    enabled: bool = True  # ON BY DEFAULT
    coverage: CoverageSettings = Field(default_factory=CoverageSettings)
    auto_approve_quality_gates: bool = True
    block_merge_on_failure: bool = True


class AgentsSettings(BaseModel):
    approver_agent: ApproverAgentSettings = Field(
        default_factory=ApproverAgentSettings
    )


class AgentSettings(BaseModel):
    agents: AgentsSettings = Field(default_factory=AgentsSettings)


_settings: Optional[AgentSettings] = None


def load_settings(config_path: Optional[Path] = None) -> AgentSettings:
    """Load settings from YAML with environment overrides."""
    if config_path is None:
        config_path = Path("agents/config/agent_settings.yaml")

    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f)
            settings = AgentSettings(**data.get("settings", {}))
    else:
        settings = AgentSettings()

    # Environment variable overrides
    if os.getenv("LATTICE_APPROVER_ENABLED", "").lower() == "false":
        settings.agents.approver_agent.enabled = False

    if target := os.getenv("LATTICE_COVERAGE_TARGET"):
        settings.agents.approver_agent.coverage.target = int(target)

    return settings


def get_settings() -> AgentSettings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def reset_settings() -> None:
    """Reset settings for testing."""
    global _settings
    _settings = None
```

---

### Phase 3: CI/CD Integration (Priority: High)

#### 3.1 GitHub Actions Workflow

```yaml
# .github/workflows/approver-agent.yml
name: Approver Agent Review

on:
  pull_request:
    branches: [main, develop]

jobs:
  approver-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run Coverage Analysis
        run: |
          pytest tests/ --cov=src/lattice_lock --cov-report=xml --cov-fail-under=90
        continue-on-error: true

      - name: Run Documentation Validation
        run: pytest tests/documentation/ -v

      - name: Run Quality Tests
        run: pytest tests/quality/ -v

      - name: Run Approver Agent
        run: |
          python -m lattice_lock.agents.approver.cli review \
            --pr ${{ github.event.pull_request.number }}

      - name: Post Review Comment
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            // Post approver agent results as PR comment
```

#### 3.2 Pre-commit Hook Integration

```yaml
# Addition to .pre-commit-config.yaml
  - repo: local
    hooks:
      - id: approver-quick-check
        name: Approver Agent Quick Check
        entry: python -m lattice_lock.agents.approver.cli quick-check
        language: system
        pass_filenames: false
        stages: [pre-push]
```

---

### Phase 4: Test Implementation (Priority: High)

#### 4.1 Documentation Tests

```python
# tests/documentation/test_markdown_links.py
"""Validate all markdown links in documentation."""

import pytest
import re
from pathlib import Path


@pytest.mark.documentation
class TestMarkdownLinks:
    """Test internal link integrity."""

    @pytest.fixture
    def markdown_files(self):
        """Collect all markdown files."""
        return list(Path(".").rglob("*.md"))

    def test_internal_links_resolve(self, markdown_files):
        """All internal links must point to existing files."""
        link_pattern = re.compile(r'\[([^\]]+)\]\((?!http)([^)#]+)')
        broken = []

        for md_file in markdown_files:
            content = md_file.read_text(errors='ignore')
            for match in link_pattern.finditer(content):
                link_path = md_file.parent / match.group(2)
                if not link_path.exists():
                    broken.append(f"{md_file}:{match.group(2)}")

        assert not broken, f"Broken links:\n" + "\n".join(broken[:20])

    def test_code_blocks_have_language(self, markdown_files):
        """Code blocks should specify language."""
        pattern = re.compile(r'^```\s*$', re.MULTILINE)
        unlabeled = []

        for md_file in markdown_files:
            content = md_file.read_text(errors='ignore')
            if matches := pattern.findall(content):
                unlabeled.append(f"{md_file}: {len(matches)} unlabeled")

        # Warning, not failure
        if unlabeled:
            pytest.skip(f"Unlabeled code blocks: {len(unlabeled)} files")
```

```python
# tests/documentation/test_code_examples.py
"""Validate Python code examples in documentation."""

import ast
import pytest
import re
from pathlib import Path


@pytest.mark.documentation
class TestCodeExamples:
    """Test code example validity."""

    def test_python_examples_parse(self):
        """All Python code blocks must be valid syntax."""
        python_block = re.compile(r'```python\n(.*?)```', re.DOTALL)
        errors = []

        for md_file in Path("docs").rglob("*.md"):
            content = md_file.read_text(errors='ignore')
            for i, match in enumerate(python_block.finditer(content)):
                code = match.group(1)
                # Skip incomplete examples with ellipsis
                if '...' in code or '# ...' in code:
                    continue
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    errors.append(f"{md_file} block {i+1}: {e.msg}")

        assert not errors, f"Invalid Python:\n" + "\n".join(errors[:10])
```

#### 4.2 Quality Tests

```python
# tests/quality/test_coverage.py
"""Validate coverage meets targets."""

import subprocess
import pytest


@pytest.mark.quality
class TestCoverageThresholds:
    """Test coverage configuration."""

    def test_coverage_target_in_config(self):
        """pyproject.toml should have 90% target."""
        import tomllib
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        fail_under = config["tool"]["coverage"]["report"]["fail_under"]
        assert fail_under == 90, f"Coverage target should be 90%, got {fail_under}%"

    def test_pytest_coverage_flag(self):
        """pytest addopts should enforce 90% coverage."""
        import tomllib
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        addopts = config["tool"]["pytest"]["ini_options"]["addopts"]
        assert "--cov-fail-under=90" in addopts
```

---

### Phase 5: Advanced Features (Priority: Medium)

#### 5.1 Mutation Testing Integration
```python
# tests/mutation/conftest.py
# Integration with mutmut for mutation testing
```

#### 5.2 Property-Based Testing Patterns
```python
# tests/properties/test_agent_properties.py
# Hypothesis-based property tests for agents
```

#### 5.3 Bug Automation GitHub Integration
```python
# src/lattice_lock/agents/bug_automation/github_client.py
# GitHub API client for issue creation
```

---

## Implementation Timeline

| Phase | Components | Estimated Effort | Dependencies |
|-------|------------|------------------|--------------|
| **Phase 1** | Settings loader, base agent, doc tests, quality tests | 2-3 days | None |
| **Phase 2** | ApproverAgent Python impl, sub-agents | 3-4 days | Phase 1 |
| **Phase 3** | CI/CD workflows, pre-commit hooks | 1-2 days | Phase 2 |
| **Phase 4** | Full test suite, coverage validation | 2-3 days | Phase 1 |
| **Phase 5** | Mutation testing, property tests, bug automation | 3-5 days | Phase 2,4 |

**Total**: ~11-17 days for full implementation

---

## Immediate Next Steps

1. **Create settings loader** (`src/lattice_lock/agents/settings.py`)
2. **Create documentation test files** (`tests/documentation/`)
3. **Create quality test files** (`tests/quality/`)
4. **Create ApproverAgent base class** (`src/lattice_lock/agents/approver/`)
5. **Add GitHub Actions workflow** (`.github/workflows/approver-agent.yml`)

---

## Architecture Improvements to Consider

### Current Weaknesses
1. **No runtime enforcement** - Settings exist but nothing reads them
2. **No actual blocking** - Approver can't actually block merges yet
3. **YAML-only agents** - Need Python implementation to execute
4. **Missing contract tests** - Agent interactions undefined

### Recommended Additions
1. **Agent Protocol** - Define abstract interface for all agents
2. **Event System** - Trigger agents on file/PR events
3. **Result Caching** - Cache analysis results for performance
4. **Incremental Analysis** - Only analyze changed files
5. **Parallel Execution** - Run sub-agents concurrently
6. **Webhook Integration** - GitHub webhooks for real-time triggers

---

## Success Criteria

The testing program is "implemented" when:

- [ ] `pytest tests/documentation/` passes
- [ ] `pytest tests/quality/` passes
- [ ] `ApproverAgent().review_pr()` executes successfully
- [ ] Coverage stays at 90%+ with new code
- [ ] CI pipeline runs approver on every PR
- [ ] Settings can be toggled via environment variables
- [ ] Pre-push hook validates quality gates
