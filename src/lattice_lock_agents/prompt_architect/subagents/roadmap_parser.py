import os

import yaml

from .parsers.roadmap_parser import (
    GanttParser,
    KanbanParser,
    RoadmapStructure,
    WorkBreakdownParser,
)


class RoadmapParser:
    def __init__(self):
        self.definition = self._load_definition()
        self.parsers = {
            "wbs": WorkBreakdownParser(),
            "gantt": GanttParser(),
            "kanban": KanbanParser(),
        }

    def _load_definition(self) -> dict:
        # Assuming the agent definition is at a fixed relative path or we can find it
        # The prompt says: agent_definitions/prompt_architect_agent/subagents/roadmap_parser.yaml
        # We are in src/lattice_lock_agents/prompt_architect/subagents/roadmap_parser.py
        # So we need to go up to root.

        # Try to find the root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up 4 levels to root: subagents -> prompt_architect -> lattice_lock_agents -> src -> root
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

        def_path = os.path.join(
            root_dir,
            "agent_definitions",
            "prompt_architect_agent",
            "subagents",
            "roadmap_parser.yaml",
        )

        if os.path.exists(def_path):
            with open(def_path) as f:
                return yaml.safe_load(f)
        return {}

    def parse(self, roadmap_path: str) -> RoadmapStructure:
        if not os.path.exists(roadmap_path):
            raise FileNotFoundError(f"Roadmap file not found: {roadmap_path}")

        # Determine format
        # For now, simplistic extension/name check
        if roadmap_path.endswith(".md") or "work_breakdown" in roadmap_path:
            parser = self.parsers["wbs"]
        else:
            # Default to WBS for now as it's the only one fully implemented
            parser = self.parsers["wbs"]

        with open(roadmap_path) as f:
            content = f.read()

        structure = parser.parse(content)

        # Post-processing: Validate and Analyze
        self._validate_structure(structure)

        return structure

    def _validate_structure(self, structure: RoadmapStructure):
        # Check for circular dependencies
        if self.detect_circular_dependencies(structure):
            raise ValueError("Circular dependency detected in roadmap")

    def get_dependency_graph(self, structure: RoadmapStructure) -> dict[str, list[str]]:
        """Returns the adjacency list of the dependency graph."""
        return structure.dependencies

    def detect_circular_dependencies(self, structure: RoadmapStructure) -> bool:
        """Detects if there are any cycles in the dependency graph."""
        graph = structure.dependencies
        visited = set()
        recursion_stack = set()

        def dfs(node):
            visited.add(node)
            recursion_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True

            recursion_stack.remove(node)
            return False

        # Check all nodes (epics)
        all_nodes = set()
        for phase in structure.phases:
            for epic in phase.epics:
                all_nodes.add(epic.id)

        for node in all_nodes:
            if node not in visited:
                if dfs(node):
                    return True

        return False

    def get_critical_path(self, structure: RoadmapStructure) -> list[str]:
        """
        Identifies the critical path.
        Since we don't have task durations in the WBS, we assume unit duration or rely on structure.
        For a proper critical path, we need durations.
        We will assume each Epic takes 1 unit of time if not specified.
        """
        graph = structure.dependencies

        # Flatten epics to a map for easy access
        epics = {}
        for phase in structure.phases:
            for epic in phase.epics:
                epics[epic.id] = epic

        # Calculate earliest start and finish
        # This requires a topological sort or relaxation

        # 1. Topological Sort
        in_degree = {u: 0 for u in epics}
        for u in graph:
            for v in graph[u]:
                if v in in_degree:
                    in_degree[v] += 1
                else:
                    # If v is not in epics (e.g. external dep), ignore or add
                    pass

        queue = [u for u in epics if in_degree[u] == 0]
        sorted_nodes = []

        while queue:
            u = queue.pop(0)
            sorted_nodes.append(u)

            if u in graph:
                for v in graph[u]:
                    if v in in_degree:
                        in_degree[v] -= 1
                        if in_degree[v] == 0:
                            queue.append(v)

        if len(sorted_nodes) != len(epics):
            # Cycle detected or disconnected components handled poorly
            return []

        # 2. Longest Path Calculation
        # dist[v] = max(dist[u] + duration[u]) for all u -> v
        dist = {u: 0 for u in epics}
        # Predecessors for path reconstruction
        predecessors = {u: None for u in epics}

        # Default duration 1
        duration = 1

        for u in sorted_nodes:
            # Update neighbors
            current_dist = dist[u] + duration
            if u in graph:
                for v in graph[u]:
                    if v in dist:
                        if current_dist > dist[v]:
                            dist[v] = current_dist
                            predecessors[v] = u

        # Find max dist
        if not dist:
            return []

        max_node = max(dist, key=dist.get)

        # Reconstruct path
        path = []
        curr = max_node
        while curr:
            path.append(curr)
            curr = predecessors[curr]

        return path[::-1]

    def get_parallel_execution_opportunities(self, structure: RoadmapStructure) -> list[list[str]]:
        """
        Identifies groups of tasks that can be executed in parallel.
        This is effectively finding tasks at the same 'level' or depth in the DAG.
        """
        graph = structure.dependencies
        epics = {}
        for phase in structure.phases:
            for epic in phase.epics:
                epics[epic.id] = epic

        in_degree = {u: 0 for u in epics}
        for u in graph:
            for v in graph[u]:
                if v in in_degree:
                    in_degree[v] += 1

        # Level order traversal (BFS)
        queue = [u for u in epics if in_degree[u] == 0]
        levels = []

        while queue:
            level_size = len(queue)
            current_level = []

            for _ in range(level_size):
                u = queue.pop(0)
                current_level.append(u)

                if u in graph:
                    for v in graph[u]:
                        if v in in_degree:
                            in_degree[v] -= 1
                            if in_degree[v] == 0:
                                queue.append(v)

            if current_level:
                levels.append(current_level)

        return levels
