"""
PLC Controller Module

Purpose:
    Receives sensor data, updates factory state,
    and evaluates industrial rules.
"""

from backend.core.logger import setup_logger

from backend.industrial.config.mqtt_config import (
    PLC_CLIENT,
    TEMPERATURE_TOPIC,
    PRESSURE_TOPIC,
    ALERT_TOPIC,
)

from backend.industrial.mqtt.subscriber import (
    MQTTSubscriber,
)

from backend.industrial.mqtt.publisher import (
    MQTTPublisher,
)

from backend.industrial.plc.rules import (
    PLCRules,
)

from backend.industrial.plc.state import (
    PLCState,
)

# ==================================================
# Cyber Attack State
# ==================================================

from backend.attacks.plc.plc_state import (
    PLCState as AttackPLCState,
)


class PLCController:
    """Virtual PLC Controller."""

    def __init__(self):

        self.logger = setup_logger(
            "PLC Controller"
        )

        self.state = PLCState()

        self.subscriber = MQTTSubscriber(
            client_id=PLC_CLIENT,
            message_handler=self.process_message,
        )

        self.publisher = MQTTPublisher(
            client_id=f"{PLC_CLIENT}_alerts"
        )

        self.previous_status = "UNKNOWN"

    # ==================================================
    # Process Incoming MQTT
    # ==================================================

    def process_message(
        self,
        topic: str,
        payload: dict,
    ):
        """
        Process incoming sensor messages.
        """

        sensor_type = payload.get(
            "sensor_type"
        )

        value = payload.get(
            "value"
        )

        # ==========================================
        # Command Injection Attack
        # ==========================================

        if AttackPLCState.command_injection:

            self.logger.warning(
                "PLC Command Injection Active -> %s",
                AttackPLCState.injected_command,
            )

        # ==========================================
        # Unauthorized Command Attack
        # ==========================================

        if AttackPLCState.unauthorized_command:

            self.logger.warning(
                "Unauthorized PLC Command Executed"
            )

        # ==========================================
        # Setpoint Manipulation Attack
        # ==========================================

        if (
            AttackPLCState.manipulated_setpoint
            is not None
            and value is not None
        ):

            value += (
                AttackPLCState.manipulated_setpoint
            )

        # ==========================================
        # Normal PLC Logic
        # ==========================================

        if sensor_type == "temperature":

            self.state.update_temperature(
                value
            )

        elif sensor_type == "pressure":

            self.state.update_pressure(
                value
            )

        status = PLCRules.evaluate(
            self.state.temperature,
            self.state.pressure,
        )

        # ==================================================
        # Alarm State Transition
        # ==================================================

        if (
            self.previous_status != "WARNING"
            and status == "WARNING"
        ):

            self.publisher.publish(
                ALERT_TOPIC,
                {
                    "event_type": "ALARM",
                    "severity": "WARNING",
                    "status": "ACTIVE",
                    "message": (
                        "Industrial operating condition "
                        "outside safe range"
                    ),
                    "temperature": self.state.temperature,
                    "pressure": self.state.pressure,
                },
            )

            self.logger.warning(
                "SCADA ALARM RAISED | Temperature=%s | Pressure=%s",
                self.state.temperature,
                self.state.pressure,
            )

        elif (
            self.previous_status == "WARNING"
            and status == "NORMAL"
        ):

            self.publisher.publish(
                ALERT_TOPIC,
                {
                    "event_type": "ALARM",
                    "severity": "INFO",
                    "status": "CLEARED",
                    "message": (
                        "Industrial operating condition "
                        "returned to normal"
                    ),
                    "temperature": self.state.temperature,
                    "pressure": self.state.pressure,
                },
            )

            self.logger.info(
                "SCADA ALARM CLEARED | Temperature=%s | Pressure=%s",
                self.state.temperature,
                self.state.pressure,
            )

        # ==================================================
        # Update PLC State
        # ==================================================

        self.state.update_status(
            status
        )

        self.previous_status = status

        self.logger.info(
            "Factory State: %s",
            self.state.get_state(),
        )

    # ==================================================
    # Lifecycle
    # ==================================================

    def start(self):

        self.subscriber.subscribe(
            TEMPERATURE_TOPIC
        )

        self.subscriber.subscribe(
            PRESSURE_TOPIC
        )

        self.logger.info(
            "PLC Controller started."
        )

    def stop(self):

        self.subscriber.disconnect()

        self.logger.info(
            "PLC Controller stopped."
        )


if __name__ == "__main__":

    plc = PLCController()

    try:

        plc.start()

        while True:
            pass

    except KeyboardInterrupt:

        plc.stop()