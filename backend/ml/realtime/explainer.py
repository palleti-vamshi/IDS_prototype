"""
Real-Time SHAP Explainer for LightX-IDS (Phase 7.4)

Provides real-time local model explanations by combining:
1. RealTimeFeatureAdapter (Phase 7.2) for causal O(1) 32-feature extraction.
2. RealTimeInferenceEngine (Phase 7.3) for XGBoost inference and thresholding.
3. ExplainabilityService (Phase 6.8) for local TreeSHAP attribution in margin space,
   95->32 feature aggregation, and human-readable operator interpretation.

Architectural Guarantees:
- Model Immutability: Uses frozen xgboost_h3_32.pkl without retraining or mutation.
- Non-Causality: Enforces descriptive model-reliance semantics; no physical causality claims.
- Additive Fidelity: Preserves margin-space additive reconstruction guarantees (|error| < 1e-4).
- Decoupled & Modular: Bridges real-time feature streaming with XAI core cleanly.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from backend.ml.config import MODEL_DIR
from backend.ml.explainability.service import (
    ExplainabilityService,
    FROZEN_H3_32_SHA256,
    compute_sha256,
)
from backend.ml.realtime.feature_adapter import RealTimeFeatureAdapter
from backend.ml.realtime.engine import RealTimeInferenceEngine
from backend.preprocessing.schemas import ParsedSensorRecord

logger = logging.getLogger(__name__)


class RealTimeExplainer:
    """
    Real-Time SHAP Explainer for streaming industrial IoT telemetry.
    """

    def __init__(
        self,
        engine: Optional[RealTimeInferenceEngine] = None,
        explainability_service: Optional[ExplainabilityService] = None,
        threshold: float = 0.35,
        verify_hash: bool = True,
    ) -> None:
        """
        Initialize the RealTimeExplainer.

        Args:
            engine: Optional pre-configured RealTimeInferenceEngine.
            explainability_service: Optional pre-configured ExplainabilityService.
            threshold: Operating decision threshold (default 0.35).
            verify_hash: Whether to assert SHA-256 match on startup.
        """
        if engine is not None:
            self.engine = engine
            self.feature_adapter = engine.feature_adapter
        else:
            self.engine = RealTimeInferenceEngine(
                threshold=threshold,
                verify_hash=verify_hash,
            )
            self.feature_adapter = self.engine.feature_adapter

        if explainability_service is not None:
            self.explainability_service = explainability_service
        else:
            self.explainability_service = ExplainabilityService(
                threshold=threshold,
                verify_hash=verify_hash,
            )

        self.threshold = float(threshold)
        self.model_path = self.engine.model_path
        self.model_sha256 = self.engine.current_model_sha256

    def reset(self) -> None:
        """Reset historical sliding windows and device states in the feature adapter."""
        self.feature_adapter.reset()

    def verify_model_integrity(self) -> bool:
        """Verify that the model file hash matches the frozen authoritative SHA-256."""
        return bool(compute_sha256(self.model_path) == FROZEN_H3_32_SHA256)

    def explain_packet(
        self,
        packet: Union[ParsedSensorRecord, Dict[str, Any], pd.Series],
        top_k: int = 5,
        check_fidelity: bool = True,
        record_id: Optional[Union[int, str]] = None,
        attack_type: Optional[str] = None,
        timestamp: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Explain a single real-time telemetry observation end-to-end:
        1. Adapt raw packet to 32 H3-32 features using RealTimeFeatureAdapter.
        2. Execute prediction and TreeSHAP attribution via ExplainabilityService.
        3. Reconstruct human-readable narrative and return structured contract.

        Args:
            packet: ParsedSensorRecord, dict, or pandas Series with telemetry fields.
            top_k: Number of top positive and negative contributors to include.
            check_fidelity: Assert margin additive fidelity (|error| < 1e-4).
            record_id: Optional identifier for caller tracking.
            attack_type: Optional ground-truth attack category for audit reference only.
            timestamp: Optional caller timestamp override.

        Returns:
            Standardized explanation contract adhering to Phase 6.8 & 7.4 specifications.
        """
        # Step 1: Input validation
        if not isinstance(packet, (ParsedSensorRecord, dict, pd.Series)):
            raise TypeError(
                f"Expected ParsedSensorRecord, dict, or pd.Series, got {type(packet)}"
            )

        if isinstance(packet, ParsedSensorRecord):
            dev_id = str(packet.device_id)
            pkt_ts = str(packet.timestamp)
            val = packet.value
        else:
            dev_id = str(packet.get("device_id", ""))
            pkt_ts = str(packet.get("timestamp", ""))
            val = packet.get("value")

        if not dev_id:
            raise ValueError("Telemetry packet must contain a valid non-empty 'device_id'.")

        try:
            float(val)
        except (TypeError, ValueError) as err:
            raise ValueError(f"Telemetry packet 'value' must be numeric, got: {val}") from err

        effective_ts = timestamp if timestamp is not None else pkt_ts

        # Step 2: Causal feature transformation in O(1) time
        feat_dict = self.feature_adapter.transform_packet(packet)

        # Step 3: Local SHAP explanation + human explanation via frozen service
        explanation_result = self.explainability_service.explain(
            observation=feat_dict,
            attack_type=attack_type,
            record_id=record_id,
            timestamp=effective_ts,
            top_k=top_k,
            check_fidelity=check_fidelity,
        )

        # Step 4: Enrich metadata with real-time packet context
        explanation_result["metadata"]["device_id"] = dev_id
        if "features_32" not in explanation_result:
            explanation_result["features_32"] = feat_dict

        return explanation_result

    def explain_features(
        self,
        features: Union[Dict[str, Any], pd.DataFrame, pd.Series],
        top_k: int = 5,
        check_fidelity: bool = True,
        record_id: Optional[Union[int, str]] = None,
        attack_type: Optional[str] = None,
        timestamp: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Explain an already-computed 32-feature vector directly without feature adaptation.
        """
        return self.explainability_service.explain(
            observation=features,
            attack_type=attack_type,
            record_id=record_id,
            timestamp=timestamp,
            top_k=top_k,
            check_fidelity=check_fidelity,
        )

    def get_model_metadata(self) -> Dict[str, Any]:
        """Return metadata describing the frozen model and explainability pipeline."""
        meta = self.explainability_service.get_model_metadata()
        meta["decision_threshold"] = self.threshold
        return meta
