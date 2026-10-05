"""
Real-Time Inference Engine for LightX-IDS (Phase 7.3)

Provides low-latency, real-time intrusion detection by combining:
1. The causal RealTimeFeatureAdapter (Phase 7.2) for O(1) feature engineering.
2. The frozen H3-32 XGBoost scikit-learn pipeline for inference.
3. The frozen 0.35 decision threshold optimized for high attack recall.

Guarantees:
- Model Immutability: Purely read-only access to xgboost_h3_32.pkl.
- Cryptographic Verification: Asserts SHA-256 immutability on initialization.
- Decoupled Design: Strict separation from MQTT networking and UI layers.
- Robust Fallbacks: Handles unknown categories via OneHotEncoder(handle_unknown='ignore').
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
import joblib
import numpy as np
import pandas as pd

from backend.ml.config import MODEL_DIR
from backend.ml.explainability.shap_local_explainer import ALL_32_FEATURES
from backend.preprocessing.schemas import ParsedSensorRecord
from backend.ml.realtime.feature_adapter import RealTimeFeatureAdapter

logger = logging.getLogger(__name__)

FROZEN_H3_32_SHA256 = (
    "3ba36c9dd2192d36182077f5f191708c279ac6020f17dd5d524429e5b63e6a58"
)
MODEL_IDENTIFIER = "xgboost_h3_32"
FEATURE_SCHEMA_VERSION = "H3-32"
DEFAULT_DECISION_THRESHOLD = 0.35


def compute_file_sha256(path: Union[str, Path]) -> str:
    """Compute the SHA-256 cryptographic hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class RealTimeInferenceEngine:
    """
    Real-Time Intrusion Detection Engine.

    Accepts single streaming telemetry observations, generates the 32 H3-32 features,
    and produces thresholded intrusion detection inferences.
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        threshold: float = DEFAULT_DECISION_THRESHOLD,
        feature_adapter: Optional[RealTimeFeatureAdapter] = None,
        verify_hash: bool = True,
    ) -> None:
        """
        Initialize the RealTimeInferenceEngine.

        Args:
            model_path: Path to the frozen xgboost_h3_32.pkl artifact.
            threshold: Operating decision threshold for attack classification (default 0.35).
            feature_adapter: Optional pre-configured RealTimeFeatureAdapter instance.
            verify_hash: Whether to assert SHA-256 cryptographic match on load.
        """
        if model_path is None:
            self.model_path = MODEL_DIR / "xgboost_h3_32.pkl"
        else:
            self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

        self.current_model_sha256 = compute_file_sha256(self.model_path)
        if verify_hash and self.current_model_sha256 != FROZEN_H3_32_SHA256:
            raise ValueError(
                f"Model SHA-256 mismatch! Found: {self.current_model_sha256}, "
                f"Expected: {FROZEN_H3_32_SHA256}"
            )

        logger.info("Loading frozen H3-32 model pipeline from: %s", self.model_path)
        self.pipeline = joblib.load(self.model_path)
        self.threshold = float(threshold)

        if feature_adapter is not None:
            self.feature_adapter = feature_adapter
        else:
            self.feature_adapter = RealTimeFeatureAdapter()

    def verify_model_integrity(self) -> bool:
        """Verify whether the loaded model matches the authoritative frozen hash."""
        return bool(compute_file_sha256(self.model_path) == FROZEN_H3_32_SHA256)

    def reset(self) -> None:
        """Reset internal feature adapter state."""
        self.feature_adapter.reset()

    def predict_packet(
        self,
        packet: Union[ParsedSensorRecord, Dict[str, Any], pd.Series],
    ) -> Dict[str, Any]:
        """
        Process one incoming telemetry packet end-to-end:
        1. Adapt to 32 H3-32 features.
        2. Evaluate XGBoost pipeline.
        3. Apply decision threshold.
        4. Return structured inference dictionary.

        Args:
            packet: ParsedSensorRecord, dict, or pandas Series with telemetry fields.

        Returns:
            Structured prediction dictionary.
        """
        # Step 1: Input validation
        if not isinstance(packet, (ParsedSensorRecord, dict, pd.Series)):
            raise TypeError(
                f"Expected ParsedSensorRecord, dict, or pd.Series, got {type(packet)}"
            )

        if isinstance(packet, ParsedSensorRecord):
            dev_id = str(packet.device_id)
            raw_ts = str(packet.timestamp)
            val = packet.value
        else:
            dev_id = str(packet.get("device_id", ""))
            raw_ts = str(packet.get("timestamp", ""))
            val = packet.get("value")

        if not dev_id:
            raise ValueError("Telemetry packet must contain a valid non-empty 'device_id'.")

        try:
            float(val)
        except (TypeError, ValueError) as err:
            raise ValueError(f"Telemetry packet 'value' must be numeric, got: {val}") from err

        # Step 2: Feature transformation
        feat_dict = self.feature_adapter.transform_packet(packet)

        # Step 3: Fast DataFrame assembly adhering to ALL_32_FEATURES order
        ordered_row = {col: [feat_dict[col]] for col in ALL_32_FEATURES}
        df_32 = pd.DataFrame(ordered_row)

        # Step 4: Model inference
        probs = self.pipeline.predict_proba(df_32)[0]
        normal_prob = float(probs[0])
        attack_prob = float(probs[1])

        # Step 5: Threshold decision
        is_attack = bool(attack_prob >= self.threshold)
        prediction_label = "ATTACK" if is_attack else "NORMAL"

        # Step 6: Assemble structured output
        return {
            "prediction": prediction_label,
            "is_attack": is_attack,
            "attack_probability": attack_prob,
            "normal_probability": normal_prob,
            "decision_threshold": self.threshold,
            "features_32": feat_dict,
            "metadata": {
                "model_identifier": MODEL_IDENTIFIER,
                "model_sha256": self.current_model_sha256,
                "feature_schema": FEATURE_SCHEMA_VERSION,
                "device_id": dev_id,
                "timestamp": raw_ts,
            },
        }

    def predict_features(
        self,
        features: Union[Dict[str, Any], pd.DataFrame, pd.Series],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate inference directly on an already-transformed 32-feature vector.
        """
        if isinstance(features, pd.DataFrame):
            df_32 = features[ALL_32_FEATURES]
            feat_dict = df_32.iloc[0].to_dict()
        elif isinstance(features, pd.Series):
            df_32 = pd.DataFrame([{col: features[col] for col in ALL_32_FEATURES}])
            feat_dict = dict(features)
        elif isinstance(features, dict):
            df_32 = pd.DataFrame([{col: features[col] for col in ALL_32_FEATURES}])
            feat_dict = dict(features)
        else:
            raise TypeError(f"Unsupported features type: {type(features)}")

        probs = self.pipeline.predict_proba(df_32)[0]
        normal_prob = float(probs[0])
        attack_prob = float(probs[1])
        is_attack = bool(attack_prob >= self.threshold)
        prediction_label = "ATTACK" if is_attack else "NORMAL"

        meta = {
            "model_identifier": MODEL_IDENTIFIER,
            "model_sha256": self.current_model_sha256,
            "feature_schema": FEATURE_SCHEMA_VERSION,
        }
        if metadata:
            meta.update(metadata)

        return {
            "prediction": prediction_label,
            "is_attack": is_attack,
            "attack_probability": attack_prob,
            "normal_probability": normal_prob,
            "decision_threshold": self.threshold,
            "features_32": feat_dict,
            "metadata": meta,
        }

    def get_model_metadata(self) -> Dict[str, Any]:
        """Return metadata describing the frozen model and inference settings."""
        return {
            "model_identifier": MODEL_IDENTIFIER,
            "model_path": str(self.model_path),
            "model_sha256": self.current_model_sha256,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "features_count": len(ALL_32_FEATURES),
            "decision_threshold": self.threshold,
            "is_immutable": bool(self.current_model_sha256 == FROZEN_H3_32_SHA256),
        }
