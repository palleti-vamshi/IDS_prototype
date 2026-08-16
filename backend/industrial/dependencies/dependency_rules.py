"""
dependency_rules.py

Industrial dependency rules for LightX-IDS.
"""

from __future__ import annotations

from backend.industrial.machines import (
    Tank,
    Pump,
    Valve,
    Conveyor,
    Motor,
    Compressor,
)


class DependencyRules:
    """
    Applies industrial dependency rules
    between connected machines.
    """

    @staticmethod
    def apply(
        machines: list,
    ) -> None:

        machine_map = {
            type(machine): machine
            for machine in machines
        }

        tank = machine_map.get(Tank)
        pump = machine_map.get(Pump)
        valve = machine_map.get(Valve)
        conveyor = machine_map.get(Conveyor)
        motor = machine_map.get(Motor)
        compressor = machine_map.get(Compressor)

        # ==========================================
        # Tank → Pump
        # ==========================================

        if tank and pump:

            if tank.level_percentage < 20:

                pump.flow_rate *= 0.5

                pump.pressure *= 0.7

        # ==========================================
        # Pump → Valve
        # ==========================================

        if pump and valve:

            if pump.flow_rate < 30:

                valve.flow_rate *= 0.6

                valve.pressure *= 0.8

        # ==========================================
        # Valve → Tank
        # ==========================================

        if valve and tank:

            if valve.position < 20:

                tank.outflow_rate *= 0.5

        # ==========================================
        # Motor → Conveyor
        # ==========================================

        if motor and conveyor:

            if motor.load > 90:

                conveyor.belt_speed *= 0.7

                conveyor.rpm *= 0.8

        # ==========================================
        # Compressor → Valve
        # ==========================================

        if compressor and valve:

            if compressor.pressure < 120:

                valve.position *= 0.8