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
                    device_id="mtr_001_temperature_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR",
                    device_id="mtr_001_current_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                RPMSensor(
                    sensor_code=f"{machine.machine_code}-RPM",
                    device_id="mtr_001_rpm_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                VibrationSensor(
                    sensor_code=f"{machine.machine_code}-VIB",
                    device_id="mtr_001_vibration_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                VoltageSensor(
                    sensor_code=f"{machine.machine_code}-VLT",
                    device_id="mtr_001_voltage_sensor",
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
                    device_id="pmp_001_pressure_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                FlowSensor(
                    sensor_code=f"{machine.machine_code}-FLW",
                    device_id="pmp_001_flow_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR",
                    device_id="pmp_001_current_sensor",
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
                    device_id="tnk_001_level_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                TemperatureSensor(
                    sensor_code=f"{machine.machine_code}-TMP",
                    device_id="tnk_001_temperature_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS",
                    device_id="tnk_001_pressure_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                HumiditySensor(
                    sensor_code=f"{machine.machine_code}-HUM",
                    device_id="tnk_001_humidity_sensor",
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
                    device_id="cnv_001_rpm_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR",
                    device_id="cnv_001_current_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                ProximitySensor(
                    sensor_code=f"{machine.machine_code}-PRX",
                    device_id="cnv_001_proximity_sensor",
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
                    device_id="vlv_001_pressure_sensor",
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
                    device_id="cmp_001_temperature_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                PressureSensor(
                    sensor_code=f"{machine.machine_code}-PRS",
                    device_id="cmp_001_pressure_sensor",
                    communication=communication,
                )
            )

            machine.attach_sensor(
                CurrentSensor(
                    sensor_code=f"{machine.machine_code}-CUR",
                    device_id="cmp_001_current_sensor",
                    communication=communication,
                )
            )