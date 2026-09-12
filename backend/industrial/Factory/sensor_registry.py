"""
sensor_registry.py

Central registry for assigning default sensors
to industrial machines.
"""

from __future__ import annotations

from backend.industrial.communication.communication_controller import (
    CommunicationController,
)

from backend.industrial.machines import (
    Motor,
    Pump,
    Valve,
    Conveyor,
    Tank,
    Compressor,
)

from backend.industrial.sensors import (
    TemperatureSensor,
    PressureSensor,
    CurrentSensor,
    VoltageSensor,
    FlowSensor,
    RPMSensor,
    VibrationSensor,
    HumiditySensor,
    LevelSensor,
    ProximitySensor,
)


class SensorRegistry:
    """
    Attaches the default sensors required by each
    industrial machine.
    """

    @staticmethod
    def attach_default_sensors(
        machine,
        communication: CommunicationController | None = None,
    ) -> None:

        # ==========================================
        # Motor
        # ==========================================

        if isinstance(machine, Motor):

            machine.attach_sensor(
                TemperatureSensor(
                    sensor_code=f"{machine.machine_code}-TMP",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                RPMSensor(
                    sensor_code=f"{machine.machine_code}-RPM",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                VibrationSensor(
                    sensor_code=f"{machine.machine_code}-VIB",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                VoltageSensor(
                    sensor_code=f"{machine.machine_code}-VLT",
                    communication=communication,
                )
            )

        # ==========================================
        # Pump
        # ==========================================

        elif isinstance(machine, Pump):

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                FlowSensor(
                    sensor_code=f"{machine.machine_code}-FLW",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR",
                    communication=communication,
                )
            )

        # ==========================================
        # Tank
        # ==========================================

        elif isinstance(machine, Tank):

            machine.attach_sensor(
                LevelSensor(
                    sensor_code=f"{machine.machine_code}-LVL",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                TemperatureSensor(
                    sensor_code=f"{machine.machine_code}-TMP",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                HumiditySensor(
                    sensor_code=f"{machine.machine_code}-HUM",
                    communication=communication,
                )
            )

        # ==========================================
        # Conveyor
        # ==========================================

        elif isinstance(machine, Conveyor):

            machine.attach_sensor(
                RPMSensor(
                    sensor_code=f"{machine.machine_code}-RPM",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                ProximitySensor(
                    sensor_code=f"{machine.machine_code}-PRX",
                    communication=communication,
                )
            )

        # ==========================================
        # Valve
        # ==========================================

        elif isinstance(machine, Valve):

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS",
                    communication=communication,
                )
            )

        # ==========================================
        # Compressor
        # ==========================================

        elif isinstance(machine, Compressor):

            machine.attach_sensor(
                TemperatureSensor(
                    sensor_code=f"{machine.machine_code}-TMP",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR",
                    communication=communication,
                )
            )