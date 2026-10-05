"""
LightX-IDS Real-Time Intrusion Detection Package (Phase 7)
"""

from backend.ml.realtime.state import (
    RealTimeStateTracker,
    DeviceHistoryState,
    GlobalHistoryState,
    FROZEN_DEVICE_STATISTICS,
)
from backend.ml.realtime.feature_adapter import RealTimeFeatureAdapter
from backend.ml.realtime.engine import (
    RealTimeInferenceEngine,
    FROZEN_H3_32_SHA256,
)
from backend.ml.realtime.explainer import RealTimeExplainer
from backend.ml.realtime.events import (
    DetectionEvent,
    EventSeverity,
    calculate_severity,
    RealTimeAlertDispatcher,
)

from backend.ml.realtime.mqtt_bridge import RealTimeMQTTBridge

__all__ = [
    "RealTimeStateTracker",
    "DeviceHistoryState",
    "GlobalHistoryState",
    "FROZEN_DEVICE_STATISTICS",
    "RealTimeFeatureAdapter",
    "RealTimeInferenceEngine",
    "RealTimeExplainer",
    "DetectionEvent",
    "EventSeverity",
    "calculate_severity",
    "RealTimeAlertDispatcher",
    "RealTimeMQTTBridge",
    "FROZEN_H3_32_SHA256",
]
