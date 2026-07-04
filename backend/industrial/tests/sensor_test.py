"""
Sensor Integration Test

Purpose:
    Runs both virtual sensors simultaneously.
"""

import threading
import time

from backend.industrial.sensors.temperature_sensor import TemperatureSensor
from backend.industrial.sensors.pressure_sensor import PressureSensor


def main():
    temperature_sensor = TemperatureSensor()
    pressure_sensor = PressureSensor()

    temperature_thread = threading.Thread(
        target=temperature_sensor.start,
        daemon=True,
    )

    pressure_thread = threading.Thread(
        target=pressure_sensor.start,
        daemon=True,
    )

    temperature_thread.start()
    pressure_thread.start()

    print("\nLightX-IDS Sensor Integration Test Running...")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping sensors...")

        temperature_sensor.stop()
        pressure_sensor.stop()


if __name__ == "__main__":
    main()