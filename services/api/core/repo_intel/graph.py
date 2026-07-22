import logging
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class DependencyGraph:
    """
    In-memory directed graph representing module dependencies and import relationships.
    Computes blast radius / impact radius when files are modified.
    """

    def __init__(self):
        # Forward edges: source_file -> set of imported target_files
        self._adjacency: Dict[str, Set[str]] = {}
        # Reverse edges: target_file -> set of source_files that import it
        self._reverse_adjacency: Dict[str, Set[str]] = {}

    def add_dependency(self, source_file: str, target_file: str) -> None:
        """Record that source_file depends on (imports) target_file."""
        if source_file not in self._adjacency:
            self._adjacency[source_file] = set()
        self._adjacency[source_file].add(target_file)

        if target_file not in self._reverse_adjacency:
            self._reverse_adjacency[target_file] = set()
        self._reverse_adjacency[target_file].add(source_file)

    def get_dependencies(self, file_path: str) -> List[str]:
        """Returns all direct dependencies (files imported by file_path)."""
        return list(self._adjacency.get(file_path, set()))

    def get_dependents(self, file_path: str) -> List[str]:
        """Returns all direct dependents (files that import file_path)."""
        return list(self._reverse_adjacency.get(file_path, set()))

    def get_impact_radius(self, file_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Computes the complete blast radius if file_path is edited or refactored.
        Recursively traverses reverse dependency edges up to max_depth.
        """
        visited: Set[str] = set()
        queue: List[tuple[str, int]] = [(file_path, 0)]
        depth_map: Dict[str, int] = {}

        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue

            visited.add(current)
            depth_map[current] = depth

            # Traverse all files importing `current`
            for dependent in self._reverse_adjacency.get(current, set()):
                if dependent not in visited:
                    queue.append((dependent, depth + 1))

        # Remove self
        visited.discard(file_path)

        return {
            "target_file": file_path,
            "total_impacted_count": len(visited),
            "impacted_files": list(visited),
            "depth_map": depth_map
        }
