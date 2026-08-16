"""
physics_engine.py

Central industrial physics engine for
the LightX-IDS Digital Twin.
"""

from __future__ import annotations

from backend.industrial.physics.dependency_engine import (
    DependencyEngine,
)


class PhysicsEngine:
    """
    Executes industrial physics updates
    every simulation cycle.
    """

    def __init__(self) -> None:

        self.dependencies = DependencyEngine()

    # ==================================================
    # Registration
    # ==================================================

    def register_machine(
        self,
        machine,
    ) -> None:

        self.dependencies.register_machine(
            machine
        )

    # ==================================================
    # Update
    # ==================================================

    def update(
        self,
        dt: float,
    ) -> None:

        self.dependencies.update(
            dt
        )

    # ==================================================
    # Status
    # ==================================================

    def get_status(self) -> dict:

        return {

            "registered": {

                "motor":
                self.dependencies.motor is not None,

                "conveyor":
                self.dependencies.conveyor is not None,

                "pump":
                self.dependencies.pump is not None,

                "valve":
                self.dependencies.valve is not None,

                "tank":
                self.dependencies.tank is not None,
            }
        }