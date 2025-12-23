import os

import pytest

from lattice_lock.agents.prompt_architect.subagents.parsers.roadmap_parser import (
    Epic,
    Phase,
    RoadmapStructure,
)
from lattice_lock.agents.prompt_architect.subagents.roadmap_parser import RoadmapParser

# Path to the actual WBS file
WBS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "project_prompts", "work_breakdown_structure.md"
)


@pytest.fixture
def parser():
    return RoadmapParser()


def test_parse_wbs_structure(parser):
    """Test parsing the actual work breakdown structure file."""
    if not os.path.exists(WBS_PATH):
        pytest.skip(f"WBS file not found at {WBS_PATH}")

    structure = parser.parse(WBS_PATH)

    assert isinstance(structure, RoadmapStructure)
    assert len(structure.phases) >= 5

    # Check Phase 1
    phase1 = next((p for p in structure.phases if p.number == 1), None)
    assert phase1 is not None
    assert phase1.name == "Foundation"
    assert len(phase1.epics) >= 4

    # Check Epic 1.1
    epic1_1 = next((e for e in phase1.epics if e.id == "1.1"), None)
    assert epic1_1 is not None
    assert epic1_1.name == "Package Model Orchestrator"
    assert epic1_1.owner == "Devin AI"


def test_dependency_graph(parser):
    """Test dependency graph construction with a synthetic structure."""
    # Create a synthetic structure for predictable testing
    structure = RoadmapStructure()

    # Phase 1
    p1 = Phase(number=1, name="P1")
    e1 = Epic(id="1.1", name="E1")
    e2 = Epic(id="1.2", name="E2")
    p1.epics = [e1, e2]

    # Phase 2
    p2 = Phase(number=2, name="P2")
    e3 = Epic(id="2.1", name="E3")
    p2.epics = [e3]

    structure.phases = [p1, p2]

    # Dependencies: 1.1 -> 2.1, 1.2 -> 2.1
    structure.dependencies = {"1.1": ["2.1"], "1.2": ["2.1"]}

    # Test circular dependency detection
    assert parser.detect_circular_dependencies(structure) == False

    # Add cycle: 2.1 -> 1.1
    structure.dependencies["2.1"] = ["1.1"]
    assert parser.detect_circular_dependencies(structure) == True


def test_critical_path(parser):
    """Test critical path calculation."""
    structure = RoadmapStructure()
    p1 = Phase(number=1, name="P1")
    e1 = Epic(id="A", name="A")
    e2 = Epic(id="B", name="B")
    e3 = Epic(id="C", name="C")
    e4 = Epic(id="D", name="D")
    p1.epics = [e1, e2, e3, e4]
    structure.phases = [p1]

    # A -> B -> D
    # A -> C -> D
    # Assume unit duration. Path length: 3 nodes (A, B, D) or (A, C, D)

    structure.dependencies = {"A": ["B", "C"], "B": ["D"], "C": ["D"]}

    path = parser.get_critical_path(structure)
    # Should be A -> B -> D or A -> C -> D
    assert path[0] == "A"
    assert path[-1] == "D"
    assert len(path) == 3


def test_parallel_execution(parser):
    """Test parallel execution opportunities."""
    structure = RoadmapStructure()
    p1 = Phase(number=1, name="P1")
    e1 = Epic(id="A", name="A")
    e2 = Epic(id="B", name="B")
    e3 = Epic(id="C", name="C")
    p1.epics = [e1, e2, e3]
    structure.phases = [p1]

    # A -> B
    # A -> C
    # B and C can be parallel

    structure.dependencies = {"A": ["B", "C"]}

    levels = parser.get_parallel_execution_opportunities(structure)
    # Level 0: [A]
    # Level 1: [B, C] (order within level doesn't matter)

    assert len(levels) == 2
    assert "A" in levels[0]
    assert "B" in levels[1]
    assert "C" in levels[1]


def test_malformed_roadmap(parser):
    """Test error handling."""
    with pytest.raises(FileNotFoundError):
        parser.parse("non_existent_file.md")
