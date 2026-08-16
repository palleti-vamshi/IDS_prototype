"""
dependency_graph.py

Industrial machine dependency graph for LightX-IDS.
"""

from __future__ import annotations


class DependencyGraph:
    """
    Represents the physical dependency relationships
    between industrial machines.
    """

    def __init__(self) -> None:

        self.graph: dict[str, list[str]] = {}

    # ==========================================
    # Registration
    # ==========================================

    def add_dependency(
        self,
        source: str,
        target: str,
    ) -> None:
        """
        Register a dependency:
        source -> target
        """

        self.graph.setdefault(
            source,
            []
        ).append(target)

    # ==========================================
    # Access
    # ==========================================

    def get_dependents(
        self,
        machine_code: str,
    ) -> list[str]:
        """
        Return all machines affected
        by this machine.
        """

        return self.graph.get(
            machine_code,
            [],
        )

    def get_graph(self) -> dict:
        """
        Return complete dependency graph.
        """

        return self.graph

    def clear(self) -> None:
        """
        Remove all dependencies.
        """

        self.graph.clear()

    def __len__(self) -> int:

        return len(self.graph)

    def __str__(self) -> str:

        return (
            f"DependencyGraph("
            f"{len(self.graph)} sources)"
        )