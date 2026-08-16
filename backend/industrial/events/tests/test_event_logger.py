from backend.industrial.events.event import (
    IndustrialEvent,
)

from backend.industrial.events.event_logger import (
    IndustrialEventLogger,
)


logger = IndustrialEventLogger(
    max_events=3
)

logger.log(
    event_type="MACHINE_STARTED",
    source="MTR-001",
    severity="INFO",
    message="Motor started.",
)

logger.log(
    event_type="HIGH_TEMPERATURE",
    source="MTR-001-TMP",
    severity="WARNING",
    message="Temperature exceeded warning threshold.",
    metadata={
        "value": 82.0,
        "unit": "°C",
    },
)

logger.log(
    event_type="MACHINE_FAULT",
    source="MTR-001",
    severity="CRITICAL",
    message="Motor entered fault state.",
)

assert logger.total_events == 3

assert len(
    logger.get_by_source("MTR-001")
) == 2

assert len(
    logger.get_by_severity("CRITICAL")
) == 1

event = logger.get_latest(1)[0]

assert isinstance(
    event,
    IndustrialEvent,
)

assert event.to_dict()["event_type"] == (
    "MACHINE_FAULT"
)

print("=" * 60)
print("🎉 INDUSTRIAL EVENT LOGGER TEST PASSED")
print("=" * 60)