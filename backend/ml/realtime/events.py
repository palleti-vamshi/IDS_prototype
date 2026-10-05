"""
Real-Time Detection Event & Alert Dispatching Layer for LightX-IDS (Phase 7.5)

Converts real-time inference and explanation results into structured security events:
1. DetectionEvent: Strongly typed data contract for detection events and alerts.
2. EventSeverity: Deterministic confidence-based classification (NORMAL, LOW, MEDIUM, HIGH).
3. RealTimeAlertDispatcher: Coordinates inference, selective SHAP explanations,
   event deduplication/rate suppression, and callback listeners for downstream consumers.

Architectural Guarantees:
- Strict Decoupling: Separates ML prediction, event classification, and explanation.
- Model Immutability: Preserves frozen H3-32 model SHA-256 and 0.35 decision threshold.
- Selective SHAP: Runs full TreeSHAP only on attacks or explicit audit requests,
  preserving the sub-2ms normal telemetry throughput established in Phase 7.3.
- No State Corruption: Uses already-extracted features for SHAP to avoid double state updates.
- Deterministic: Output fields and severity mappings are 100% reproducible.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union
import uuid

import numpy as np
import pandas as pd

from backend.ml.realtime.engine import (
    RealTimeInferenceEngine,
    FROZEN_H3_32_SHA256,
    DEFAULT_DECISION_THRESHOLD,
    MODEL_IDENTIFIER,
)
from backend.ml.realtime.explainer import RealTimeExplainer
from backend.preprocessing.schemas import ParsedSensorRecord

logger = logging.getLogger(__name__)

MODEL_VERSION = "Phase 5 Frozen (Seed 42)"


class EventSeverity(str, Enum):
    """
    Deterministic severity categories based strictly on model attack probability.
    Does not make physical or clinical safety claims.
    """
    NORMAL = "NORMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


def calculate_severity(attack_probability: float, threshold: float = DEFAULT_DECISION_THRESHOLD) -> str:
    """
    Calculate deterministic event severity based on model confidence:
    - [0.00, threshold) -> NORMAL
    - [threshold, 0.60) -> LOW
    - [0.60, 0.85)     -> MEDIUM
    - [0.85, 1.00]     -> HIGH

    Args:
        attack_probability: Float probability in [0.0, 1.0].
        threshold: Decision threshold (default 0.35).

    Returns:
        String severity value from EventSeverity.
    """
    prob = float(attack_probability)
    if prob < threshold:
        return EventSeverity.NORMAL.value
    elif prob < 0.60:
        return EventSeverity.LOW.value
    elif prob < 0.85:
        return EventSeverity.MEDIUM.value
    else:
        return EventSeverity.HIGH.value


def _to_serializable(val: Any) -> Any:
    """Recursively convert numpy types to standard Python primitives."""
    if isinstance(val, (np.floating, float)):
        return float(val)
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, dict):
        return {k: _to_serializable(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [_to_serializable(v) for v in val]
    return val


@dataclass
class DetectionEvent:
    """
    LightX-IDS Detection Event Schema.

    Represents a single evaluated telemetry observation and its associated
    security classification, metadata, and optional SHAP explanation.
    """
    event_id: str
    timestamp: str
    prediction: str                      # "ATTACK" | "NORMAL"
    is_attack: bool                       # True if attack_probability >= decision_threshold
    attack_probability: float             # P(Attack)
    normal_probability: float             # P(Normal)
    decision_threshold: float             # Frozen at 0.35
    severity: str                         # NORMAL | LOW | MEDIUM | HIGH
    device_id: str
    sensor_code: Optional[str] = None
    sensor_type: Optional[str] = None
    topic: Optional[str] = None
    record_id: Optional[Union[int, str]] = None
    model_id: str = MODEL_IDENTIFIER
    model_version: str = MODEL_VERSION
    model_sha256: str = FROZEN_H3_32_SHA256
    is_duplicate: bool = False
    is_suppressed: bool = False
    explanation: Optional[Dict[str, Any]] = None
    human_readable: Optional[Dict[str, Any]] = None
    features_32: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the detection event to a JSON-serializable dictionary."""
        d = asdict(self)
        return _to_serializable(d)

    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize event to a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectionEvent":
        """Reconstruct a DetectionEvent from a dictionary."""
        return cls(**data)


class RealTimeAlertDispatcher:
    """
    Real-Time Alert Dispatcher & Detection Event Coordinator.

    Manages:
    1. Real-time inference via RealTimeInferenceEngine.
    2. Event creation and confidence-based severity calculation.
    3. Selective SHAP explanation triggering via RealTimeExplainer.
    4. Optional deduplication / cooldown suppression for rapid repeated alerts.
    5. Event listener callbacks for future Phase 7.6 MQTT publishing or Phase 8 UI.
    """

    def __init__(
        self,
        engine: Optional[RealTimeInferenceEngine] = None,
        explainer: Optional[RealTimeExplainer] = None,
        threshold: float = DEFAULT_DECISION_THRESHOLD,
        explain_mode: str = "on_attack",
        dedup_window_seconds: float = 0.0,
        verify_hash: bool = True,
    ) -> None:
        """
        Initialize the RealTimeAlertDispatcher.

        Args:
            engine: Optional pre-configured RealTimeInferenceEngine.
            explainer: Optional pre-configured RealTimeExplainer.
            threshold: Operating decision threshold (default 0.35).
            explain_mode: Policy for triggering SHAP explanations:
                          - 'on_attack': Only explain when is_attack is True (default).
                          - 'always': Explain every incoming packet.
                          - 'never': Never calculate SHAP (pure lightweight mode).
                          - 'on_demand': Explain only when explicitly requested by caller.
            dedup_window_seconds: Cooldown in seconds for suppressing repeated alerts
                                  for the same device (default 0.0 = event-per-detection).
            verify_hash: Whether to assert cryptographic match against frozen model hash.
        """
        if engine is not None:
            self.engine = engine
        else:
            self.engine = RealTimeInferenceEngine(
                threshold=threshold,
                verify_hash=verify_hash,
            )

        if explainer is not None:
            self.explainer = explainer
        else:
            # Explainer shares the engine and its feature adapter
            self.explainer = RealTimeExplainer(
                engine=self.engine,
                threshold=threshold,
                verify_hash=verify_hash,
            )

        self.threshold = float(threshold)
        self.explain_mode = explain_mode
        self.dedup_window_seconds = float(dedup_window_seconds)

        # Alert listeners: (event: DetectionEvent) -> None
        self._all_event_listeners: List[Callable[[DetectionEvent], None]] = []
        self._alert_listeners: List[Callable[[DetectionEvent], None]] = []

        # Deduplication tracking: (device_id, sensor_type) -> last_alert_time
        self._last_alert_times: Dict[str, float] = {}

    def reset(self) -> None:
        """Reset internal feature adapter state and deduplication tracking."""
        self.engine.reset()
        self._last_alert_times.clear()

    def subscribe(self, listener: Callable[[DetectionEvent], None]) -> None:
        """Subscribe a listener to all generated detection events (NORMAL and ATTACK)."""
        self._all_event_listeners.append(listener)

    def subscribe_alerts(self, listener: Callable[[DetectionEvent], None]) -> None:
        """Subscribe a listener to unsuppressed ATTACK alerts only."""
        self._alert_listeners.append(listener)

    def _should_explain(self, is_attack: bool, explicit_explain: Optional[bool]) -> bool:
        """Determine whether to trigger SHAP explanation for the current packet."""
        if explicit_explain is not None:
            return bool(explicit_explain)

        if self.explain_mode == "always":
            return True
        elif self.explain_mode == "on_attack":
            return bool(is_attack)
        elif self.explain_mode in ("never", "on_demand"):
            return False
        return False

    def _check_deduplication(self, device_id: str, sensor_type: Optional[str], event_timestamp: float) -> bool:
        """
        Check if an alert should be suppressed due to deduplication cooldown window.
        Returns True if suppressed (duplicate), False otherwise.
        """
        if self.dedup_window_seconds <= 0.0:
            return False

        key = f"{device_id}:{sensor_type or ''}"
        last_time = self._last_alert_times.get(key)
        if last_time is not None:
            elapsed = event_timestamp - last_time
            if 0.0 <= elapsed < self.dedup_window_seconds:
                return True

        self._last_alert_times[key] = event_timestamp
        return False

    def process_packet(
        self,
        packet: Union[ParsedSensorRecord, Dict[str, Any], pd.Series],
        explain: Optional[bool] = None,
        record_id: Optional[Union[int, str]] = None,
        event_id: Optional[str] = None,
        top_k: int = 5,
        attack_type: Optional[str] = None,
    ) -> DetectionEvent:
        """
        Process a single incoming telemetry packet through the detection and alert pipeline:
        1. Adapt features and run frozen XGBoost inference.
        2. Determine attack status and compute deterministic severity.
        3. Check deduplication / suppression rules.
        4. Selectively compute TreeSHAP explanation if triggered.
        5. Build structured DetectionEvent and dispatch to registered listeners.

        Args:
            packet: Incoming telemetry observation.
            explain: Explicit override to force SHAP explanation (True/False/None).
            record_id: Optional identifier for dataset/stream tracking.
            event_id: Optional explicit event identifier for deterministic replay.
            top_k: Top-K feature contributors to include if explained.
            attack_type: Optional ground-truth label for audit logs.

        Returns:
            Structured DetectionEvent object.
        """
        # Step 1: Input extraction & metadata harvesting
        if isinstance(packet, ParsedSensorRecord):
            dev_id = str(packet.device_id)
            raw_ts = str(packet.timestamp)
            sensor_code = packet.sensor_code
            sensor_type = packet.sensor_type
            topic = packet.topic
            rec_id = record_id
        elif isinstance(packet, dict):
            dev_id = str(packet.get("device_id", ""))
            raw_ts = str(packet.get("timestamp", ""))
            sensor_code = packet.get("sensor_code")
            sensor_type = packet.get("sensor_type")
            topic = packet.get("topic")
            rec_id = record_id if record_id is not None else packet.get("record_id")
        elif isinstance(packet, pd.Series):
            dev_id = str(packet.get("device_id", ""))
            raw_ts = str(packet.get("timestamp", ""))
            sensor_code = packet.get("sensor_code") if "sensor_code" in packet else None
            sensor_type = packet.get("sensor_type") if "sensor_type" in packet else None
            topic = packet.get("topic") if "topic" in packet else None
            rec_id = record_id if record_id is not None else packet.get("record_id")
        else:
            raise TypeError(
                f"Expected ParsedSensorRecord, dict, or pd.Series, got {type(packet)}"
            )

        # Step 2: Real-time inference (Feature extraction + XGBoost scoring)
        # Note: predict_packet() automatically updates the feature adapter's causal rolling state
        inference_result = self.engine.predict_packet(packet)

        is_attack = inference_result["is_attack"]
        attack_prob = inference_result["attack_probability"]
        normal_prob = inference_result["normal_probability"]
        features_32 = inference_result["features_32"]

        # Step 3: Deterministic severity calculation
        severity = calculate_severity(attack_prob, threshold=self.threshold)

        # Step 4: Event identification
        if event_id is not None:
            final_event_id = str(event_id)
        elif rec_id is not None:
            final_event_id = f"evt_{rec_id}"
        else:
            final_event_id = f"evt_{uuid.uuid4().hex[:12]}"

        # Step 5: Deduplication check
        # Try to parse timestamp as float for cooldown window, fallback to time.time()
        try:
            ts_float = float(raw_ts)
        except (ValueError, TypeError):
            ts_float = time.time()

        is_suppressed = False
        is_duplicate = False
        if is_attack:
            if self._check_deduplication(dev_id, sensor_type, ts_float):
                is_suppressed = True
                is_duplicate = True

        # Step 6: Selective SHAP explanation
        explanation_data: Optional[Dict[str, Any]] = None
        human_readable_data: Optional[Dict[str, Any]] = None

        if self._should_explain(is_attack, explain):
            # Pass the already-computed 32 features to avoid re-adapting or corrupting state
            expl_res = self.explainer.explain_features(
                features=features_32,
                top_k=top_k,
                check_fidelity=True,
                record_id=rec_id,
                attack_type=attack_type,
                timestamp=raw_ts,
            )
            explanation_data = expl_res.get("explanation")
            human_readable_data = expl_res.get("human_readable")

        # Step 7: Construct DetectionEvent
        event = DetectionEvent(
            event_id=final_event_id,
            timestamp=raw_ts,
            prediction="ATTACK" if is_attack else "NORMAL",
            is_attack=is_attack,
            attack_probability=attack_prob,
            normal_probability=normal_prob,
            decision_threshold=self.threshold,
            severity=severity,
            device_id=dev_id,
            sensor_code=sensor_code,
            sensor_type=sensor_type,
            topic=topic,
            record_id=rec_id,
            model_id=MODEL_IDENTIFIER,
            model_version=MODEL_VERSION,
            model_sha256=self.engine.current_model_sha256,
            is_duplicate=is_duplicate,
            is_suppressed=is_suppressed,
            explanation=explanation_data,
            human_readable=human_readable_data,
            features_32=features_32,
            metadata={
                "attack_type": attack_type,
                "explain_mode": self.explain_mode,
                "has_explanation": bool(explanation_data is not None),
            },
        )

        # Step 8: Dispatch to listeners
        for listener in self._all_event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error("Error in event listener callback: %s", e)

        if is_attack and not is_suppressed:
            for alert_listener in self._alert_listeners:
                try:
                    alert_listener(event)
                except Exception as e:
                    logger.error("Error in alert listener callback: %s", e)

        return event
