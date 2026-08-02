"""
sensor_registry.py

Central registry for assigning default sensors
to industrial machines.
"""

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
    def attach_default_sensors(machine) -> None:

        # ==========================================
        # Motor
        # ==========================================

        if isinstance(machine, Motor):

            machine.attach_sensor(
                TemperatureSensor(
                    sensor_code=f"{machine.machine_code}-TMP"
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR"
                )
            )

            machine.attach_sensor(
                RPMSensor(
                    sensor_code=f"{machine.machine_code}-RPM"
                )
            )

            machine.attach_sensor(
                VibrationSensor(
                    sensor_code=f"{machine.machine_code}-VIB"
                )
            )

        # ==========================================
        # Pump
        # ==========================================

        elif isinstance(machine, Pump):

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS"
                )
            )

            machine.attach_sensor(
                FlowSensor(
                    sensor_code=f"{machine.machine_code}-FLW"
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR"
                )
            )

        # ==========================================
        # Tank
        # ==========================================

        elif isinstance(machine, Tank):

            machine.attach_sensor(
                LevelSensor(
                    sensor_code=f"{machine.machine_code}-LVL"
                )
            )

            machine.attach_sensor(
                TemperatureSensor(
                    sensor_code=f"{machine.machine_code}-TMP"
                )
            )

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS"
                )
            )

        # ==========================================
        # Conveyor
        # ==========================================

        elif isinstance(machine, Conveyor):

            machine.attach_sensor(
                RPMSensor(
                    sensor_code=f"{machine.machine_code}-RPM"
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR"
                )
            )

            machine.attach_sensor(
                ProximitySensor(
                    sensor_code=f"{machine.machine_code}-PRX"
                )
            )

        # ==========================================
        # Valve
        # ==========================================

        elif isinstance(machine, Valve):

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS"
                )
            )

        # ==========================================
        # Compressor
        # ==========================================

        elif isinstance(machine, Compressor):

            machine.attach_sensor(
                TemperatureSensor(
                    sensor_code=f"{machine.machine_code}-TMP"
                )
            )

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS"
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR"
                )
            )