"""
process_models.py

Industrial process physics models used by the
LightX-IDS Digital Twin.
"""

from __future__ import annotations


class ProcessModels:
    """
    Collection of reusable industrial process models.
    """

    @staticmethod
    def calculate_tank_level(
        current_level: float,
        inflow: float,
        outflow: float,
        dt: float,
        capacity: float,
    ) -> float:
        """
        Tank level update.
        """

        level = current_level + (
            inflow - outflow
        ) * dt

        return max(
            0.0,
            min(
                capacity,
                level,
            ),
        )

    @staticmethod
    def calculate_flow(
        pump_flow: float,
        valve_position: float,
    ) -> float:
        """
        Valve restricts pump flow.
        """

        return (
            pump_flow
            * (valve_position / 100.0)
        )

    @staticmethod
    def calculate_pressure(
        flow_rate: float,
        valve_position: float,
    ) -> float:
        """
        Simple pressure model.
        """

        restriction = max(
            0.1,
            valve_position / 100.0,
        )

        return flow_rate / restriction

    @staticmethod
    def calculate_motor_load(
        conveyor_load: float,
    ) -> float:
        """
        Conveyor load affects motor load.
        """

        return min(
            100.0,
            conveyor_load,
        )

    @staticmethod
    def calculate_pump_efficiency(
        motor_health: float,
    ) -> float:
        """
        Pump efficiency decreases as
        motor health decreases.
        """

        return max(
            0.5,
            motor_health / 100.0,
        )

    @staticmethod
    def calculate_temperature(
        current_temp: float,
        power: float,
        ambient_temp: float,
        dt: float,
    ) -> float:
        """
        Simple heating/cooling model.
        """

        heating = power * 0.08

        cooling = (
            current_temp
            - ambient_temp
        ) * 0.015

        return (
            current_temp
            + heating * dt
            - cooling * dt
        )