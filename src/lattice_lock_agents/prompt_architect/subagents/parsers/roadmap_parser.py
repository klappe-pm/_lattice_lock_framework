from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import re

class Task(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    epic_id: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    estimated_hours: Optional[float] = None
    owner: Optional[str] = None
    status: Optional[str] = None

class Epic(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    tasks: List[Task] = Field(default_factory=list)
    owner: Optional[str] = None

class Phase(BaseModel):
    number: int
    name: str
    duration: Optional[str] = None
    exit_criteria: List[str] = Field(default_factory=list)
    epics: List[Epic] = Field(default_factory=list)

class RoadmapStructure(BaseModel):
    phases: List[Phase] = Field(default_factory=list)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)

class BaseRoadmapParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> RoadmapStructure:
        pass

class WorkBreakdownParser(BaseRoadmapParser):
    def parse(self, content: str) -> RoadmapStructure:
        structure = RoadmapStructure()
        lines = content.split('\n')
        current_phase: Optional[Phase] = None
        current_section = None

        # Regex patterns
        phase_pattern = re.compile(r'### Phase (\d+): (.+) \((.+)\)')
        epic_row_pattern = re.compile(r'\|\s*(\d+\.\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')
        dependency_header_pattern = re.compile(r'### Phase \d+ Dependencies')
        dependency_item_pattern = re.compile(r'Epic (\d+\.\d+) .*depends on.*') # Simplified, needs robust parsing

        # More robust dependency parsing
        # Example: "1. Epic 1.1 (Package Orchestrator) - No dependencies, start first"
        # Example: "- Epic 2.4 (Sheriff) depends on 2.1 (GitHub Actions) for CI integration"

        for line in lines:
            line = line.strip()

            # Phase detection
            phase_match = phase_pattern.match(line)
            if phase_match:
                if current_phase:
                    structure.phases.append(current_phase)

                phase_num = int(phase_match.group(1))
                phase_name = phase_match.group(2)
                duration = phase_match.group(3)
                current_phase = Phase(number=phase_num, name=phase_name, duration=duration)
                current_section = "phase_content"
                continue

            # Exit Criteria
            if "**Exit Criteria:**" in line:
                current_section = "exit_criteria"
                continue

            if current_section == "exit_criteria" and line.startswith("- ") and current_phase:
                current_phase.exit_criteria.append(line[2:])
                continue

            # Epic Table
            if line.startswith("| Epic |"):
                current_section = "epics"
                continue

            if current_section == "epics" and line.startswith("|") and not line.startswith("|---"):
                epic_match = epic_row_pattern.match(line)
                if epic_match and current_phase:
                    epic_id = epic_match.group(1).strip()
                    description = epic_match.group(2).strip()
                    owner = epic_match.group(3).strip()

                    # In WBS, Epics are high level. We treat them as Epics.
                    # Tasks might be implied or parsed from separate files, but here we just parse the WBS.
                    # The prompt says "Extract epics and tasks". In WBS md, we only have Epics in the table.
                    # Maybe we create a default task for the epic? Or just leave tasks empty.
                    # The prompt says "Parse epics with owner tool assignments".

                    epic = Epic(id=epic_id, name=description, description=description, owner=owner)
                    current_phase.epics.append(epic)
                continue

            # Dependencies
            if "## Dependencies" in line:
                if current_phase:
                    structure.phases.append(current_phase)
                    current_phase = None
                current_section = "dependencies"
                continue

            if current_section == "dependencies":
                # Parse dependencies
                # Format: "Epic X.Y ... depends on ..."
                # Or "1. Epic X.Y ... - No dependencies"

                # Simple extraction of "Epic A depends on B" logic
                # This is tricky with natural language.
                # Let's look for "Epic (\d+\.\d+)" and "depends on ([\d\.,\sand]+)"
                # Or explicit "Epic 5.3 ... depends on 5.1 and 5.2"

                # Regex for "Epic <id> ... depends on <id_list>"
                # We can iterate over all known epic IDs and see if they are mentioned as source and target.
                pass

        if current_phase:
            structure.phases.append(current_phase)

        # Second pass for dependencies (or just parse them now)
        # Let's implement a specific dependency parser for the "Dependencies" section
        self._parse_dependencies(content, structure)

        return structure

    def _parse_dependencies(self, content: str, structure: RoadmapStructure):
        # Extract the dependencies section
        try:
            dep_section = content.split("## Dependencies")[1]
        except IndexError:
            return

        lines = dep_section.split('\n')
        current_phase_deps = None

        for line in lines:
            line = line.strip()
            # Identify the subject epic
            # "Epic 5.2 ... depends on ..."
            # "1. Epic 1.1 ... - No dependencies"

            subject_match = re.search(r'Epic (\d+\.\d+)', line)
            if subject_match:
                subject_id = subject_match.group(1)

                # Check for "depends on"
                if "depends on" in line:
                    # Extract targets
                    # "depends on 5.1 and 5.2"
                    # "depends on Phase 1 completion" -> This is a phase dependency, maybe ignore or map to all phase 1 epics?
                    # "depends on 2.1 (GitHub Actions)"

                    # Find all other epic IDs in the line after "depends on"
                    after_depends = line.split("depends on")[1]
                    target_ids = re.findall(r'(\d+\.\d+)', after_depends)

                    # Also handle "depends on Phase X completion"
                    phase_dep_match = re.search(r'Phase (\d+) completion', after_depends)
                    if phase_dep_match:
                        phase_num = int(phase_dep_match.group(1))
                        # Find all epics in that phase
                        for phase in structure.phases:
                            if phase.number == phase_num:
                                for epic in phase.epics:
                                    target_ids.append(epic.id)

                    if subject_id not in structure.dependencies:
                        structure.dependencies[subject_id] = []

                    for target_id in target_ids:
                        if target_id != subject_id and target_id not in structure.dependencies[subject_id]:
                            structure.dependencies[subject_id].append(target_id)

                # Handle "All Phase X epics depend on Phase Y completion"
                # "All Phase 5 epics depend on Phase 1 completion"

            if line.startswith("- All Phase") or line.startswith("All Phase"):
                # "All Phase 5 epics depend on Phase 1 completion"
                phase_match = re.search(r'Phase (\d+) epics depend on Phase (\d+) completion', line)
                if phase_match:
                    subject_phase_num = int(phase_match.group(1))
                    target_phase_num = int(phase_match.group(2))

                    subject_epics = []
                    target_epics = []

                    for phase in structure.phases:
                        if phase.number == subject_phase_num:
                            subject_epics = [e.id for e in phase.epics]
                        if phase.number == target_phase_num:
                            target_epics = [e.id for e in phase.epics]

                    for s_id in subject_epics:
                        if s_id not in structure.dependencies:
                            structure.dependencies[s_id] = []
                        for t_id in target_epics:
                            if t_id not in structure.dependencies[s_id]:
                                structure.dependencies[s_id].append(t_id)


class GanttParser(BaseRoadmapParser):
    def parse(self, content: str) -> RoadmapStructure:
        # Placeholder for Gantt chart parsing
        return RoadmapStructure()

class KanbanParser(BaseRoadmapParser):
    def parse(self, content: str) -> RoadmapStructure:
        # Placeholder for Kanban board parsing
        return RoadmapStructure()
