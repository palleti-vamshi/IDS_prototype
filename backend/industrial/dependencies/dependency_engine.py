"""
dependency_engine.py

Central machine dependency engine for LightX-IDS.
"""

from __future__ import annotations

from backend.industrial.dependencies.dependency_graph import (
    DependencyGraph,
)

from backend.industrial.dependencies.dependency_rules import (
    DependencyRules,
)


class DependencyEngine:
    """
    Evaluates industrial dependencies
    between machines every simulation cycle.
    """

    def __init__(self) -> None:

        self.graph = DependencyGraph()

        self.machines = []

    # ==========================================
    # Registration
    # ==========================================

    def register_machine(
        self,
        machine,
    ) -> None:

        self.machines.append(machine)

    def register_dependency(
        self,
        source: str,
        target: str,
    ) -> None:

        self.graph.add_dependency(
            source,
            target,
        )

    # ==========================================
    # Update
    # ==========================================

    def update(
        self,
        dt: float,
    ) -> None:

        DependencyRules.apply(
            self.machines,
        )

    # ==========================================
    # Access
    # ==========================================

    @property
    def total_machines(
        self,
    ) -> int:

        return len(self.machines)

    @property
    def total_dependencies(
        self,
    ) -> int:

        return len(self.graph)

    def clear(
        self,
    ) -> None:

        self.machines.clear()

        self.graph.clear()

    def get_status(
        self,
    ) -> dict:

        return {

            "registered_machines":
                self.total_machines,

            "dependency_sources":
                self.total_dependencies,

            "graph":
                self.graph.get_graph(),

        }

    def __str__(
        self,
    ) -> str:

        return (

            f"DependencyEngine("

            f"machines={self.total_machines}, "

            f"dependencies={self.total_dependencies})"

        )