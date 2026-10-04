"""
LightX-IDS Explainability Service Facade

Provides the unified, high-level integration interface for the Phase 6 Explainability Subsystem.
Orchestrates prediction, local TreeExplainer SHAP calculations, 95->32 feature aggregation,
and human-readable control room narratives into a standardized, stable API contract.

Architectural Guarantees:
- Model Immutability: Purely read-only inference on frozen xgboost_h3_32.pkl.
- Non-Causality: Enforces descriptive model-reliance semantics; no physical causality claims.
- Zero Leakage: No training, fitting, or threshold adjustment during execution.
- SOLID & Backward-Compatible: Clean facade decoupling explainability core from future API/UI layers.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from backend.ml.config import MODEL_DIR
from backend.ml.explainability.shap_local_explainer import (
    LocalShapExplainer,
    ALL_32_FEATURES,
    ACTIVE_NUMERIC_COLUMNS,
    ACTIVE_CATEGORICAL_COLUMNS,
)
from backend.ml.explainability.human_explainer import (
    HumanReadableExplainer,
    EXPLANATION_LIMITATIONS,
)

logger = logging.getLogger(__name__)

FROZEN_H3_32_SHA256 = (
    "3ba36c9dd2192d36182077f5f191708c279ac6020f17dd5d524429e5b63e6a58"
)
MODEL_IDENTIFIER = "xgboost_h3_32"
FEATURE_SCHEMA_VERSION = "H3-32"
EXPLAINABILITY_METHOD = "TreeExplainer (Log-Odds Margin Space with Categorical Aggregation)"


def compute_sha256(path: Union[str, Path]) -> str:
    """Compute SHA-256 cryptographic hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class ExplainabilityService:
    """
    Unified Explainability Service Facade for LightX-IDS.

    Serves as the single integration boundary for upstream consumers (e.g. FastAPI endpoints,
    MQTT consumers, or real-time control room dashboards).
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        threshold: float = 0.35,
        verify_hash: bool = True,
    ):
        """
        Initialize the ExplainabilityService.

        Args:
            model_path: Path to the frozen xgboost_h3_32.pkl model. Defaults to authoritative model path.
            threshold: Classification decision threshold for attack alert. Defaults to frozen 0.35.
            verify_hash: Whether to verify model cryptographic immutability on startup. Default True.
        """
        if model_path is None:
            self.model_path = MODEL_DIR / "xgboost_h3_32.pkl"
        else:
            self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

        self.current_model_sha256 = compute_sha256(self.model_path)
        if verify_hash and self.current_model_sha256 != FROZEN_H3_32_SHA256:
            logger.warning(
                "Model SHA-256 (%s) differs from authoritative frozen hash (%s)",
                self.current_model_sha256,
                FROZEN_H3_32_SHA256,
            )

        self.threshold = float(threshold)
        logger.info("Initializing LocalShapExplainer for %s...", self.model_path.name)
        self.local_explainer = LocalShapExplainer(
            model_path=self.model_path, threshold=self.threshold
        )
        self.human_explainer = HumanReadableExplainer(
            local_explainer=self.local_explainer
        )

    def get_model_metadata(self) -> Dict[str, Any]:
        """Return metadata describing the frozen model and explainability pipeline."""
        return {
            "model_identifier": MODEL_IDENTIFIER,
            "model_path": str(self.model_path),
            "model_sha256": self.current_model_sha256,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "original_features_count": len(ALL_32_FEATURES),
            "original_numeric_count": len(ACTIVE_NUMERIC_COLUMNS),
            "original_categorical_count": len(ACTIVE_CATEGORICAL_COLUMNS),
            "transformed_features_count": len(self.local_explainer.transformed_feature_names),
            "decision_threshold": self.threshold,
            "explainability_method": EXPLAINABILITY_METHOD,
            "is_immutable": bool(self.current_model_sha256 == FROZEN_H3_32_SHA256),
        }

    def explain(
        self,
        observation: Union[Dict[str, Any], pd.Series, pd.DataFrame],
        attack_type: Optional[str] = None,
        record_id: Optional[Union[int, str]] = None,
        timestamp: Optional[Any] = None,
        top_k: int = 5,
        check_fidelity: bool = True,
    ) -> Dict[str, Any]:
        """
        Explain a single industrial telemetry observation.

        Args:
            observation: Telemetry observation containing the 32 H3-32 features.
            attack_type: Optional recorded ground-truth attack category (for context only).
            record_id: Optional unique identifier for the observation.
            timestamp: Optional telemetry timestamp string.
            top_k: Number of positive and negative contributors to include. Default 5.
            check_fidelity: Whether to assert mathematical additive fidelity (< 1e-4). Default True.

        Returns:
            Standardized explanation dictionary adhering to the Phase 6.8 Output Contract.
        """
        # Step 1: Compute local SHAP explanation
        local_res = self.local_explainer.explain_instance(
            observation=observation,
            top_k=top_k,
            check_fidelity=check_fidelity,
        )

        # Step 2: Compute human-readable explanation
        human_res = self.human_explainer.explain(
            local_explanation=local_res,
            attack_type=attack_type,
            record_id=record_id,
        )

        # Step 3: Package into stable integration contract
        rec_id = record_id if record_id is not None else human_res.get("record_id")
        ts_str = str(timestamp) if timestamp is not None else None

        output_contract = {
            "prediction": {
                "label": local_res["prediction"],
                "is_attack": bool(local_res["prediction"] == "ATTACK"),
                "attack_probability": float(local_res["attack_probability"]),
                "normal_probability": float(local_res["normal_probability"]),
                "raw_margin": float(local_res["raw_margin"]),
                "decision_threshold": self.threshold,
            },
            "explanation": {
                "raw_margin": float(local_res["raw_margin"]),
                "base_value": float(local_res["base_value"]),
                "reconstructed_margin": float(local_res["reconstructed_margin"]),
                "fidelity_error": float(local_res["fidelity_error"]),
                "top_attack_contributors": human_res["top_attack_contributors"],
                "top_normal_contributors": human_res["top_normal_contributors"],
                "all_contributions_32": local_res["all_contributions_32"],
                "transformed_contributions_95": local_res["shap_values_95"],
            },
            "human_readable": {
                "summary": human_res["summary"],
                "confidence_category": human_res["confidence_category"],
                "is_borderline": human_res["is_borderline"],
                "operator_interpretation": human_res["operator_interpretation"],
                "console_view": human_res["text"],
            },
            "metadata": {
                "record_id": rec_id,
                "timestamp": ts_str,
                "recorded_attack_type": human_res["attack_type"],
                "ground_truth_context": human_res["ground_truth_context"],
                "model_identifier": MODEL_IDENTIFIER,
                "model_sha256": self.current_model_sha256,
                "feature_schema_version": FEATURE_SCHEMA_VERSION,
                "explainability_method": EXPLAINABILITY_METHOD,
                "limitations": list(EXPLANATION_LIMITATIONS),
            },
        }

        return output_contract

    def verify_model_integrity(self) -> bool:
        """
        Verify whether the currently loaded model's cryptographic hash matches the authoritative frozen hash.

        Returns:
            True if SHA-256 matches exactly, False otherwise.
        """
        return bool(compute_sha256(self.model_path) == FROZEN_H3_32_SHA256)

    def explain_record(
        self,
        observation: Union[Dict[str, Any], pd.Series, pd.DataFrame],
        attack_type: Optional[str] = None,
        record_id: Optional[Union[int, str]] = None,
        timestamp: Optional[Any] = None,
        top_k: int = 5,
        check_fidelity: bool = True,
        recorded_attack_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convenience alias for explain() conforming to integration guidelines.
        """
        eff_attack_type = attack_type if attack_type is not None else recorded_attack_type
        return self.explain(
            observation=observation,
            attack_type=eff_attack_type,
            record_id=record_id,
            timestamp=timestamp,
            top_k=top_k,
            check_fidelity=check_fidelity,
        )

    def explain_dataframe(
        self,
        observations_df: pd.DataFrame,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Convenience alias for explain_batch() conforming to integration guidelines.
        """
        return self.explain_batch(observations_df=observations_df, top_k=top_k)

    def explain_batch(
        self,
        observations_df: pd.DataFrame,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of telemetry observations and return a list of explanation objects.
        """
        results = []
        for idx, row in observations_df.iterrows():
            rec_id = row.get("record_id", idx)
            att_type = row.get("attack_type", None)
            ts = row.get("timestamp", None)
            exp = self.explain(
                observation=row,
                attack_type=att_type if pd.notna(att_type) else None,
                record_id=rec_id if pd.notna(rec_id) else None,
                timestamp=ts if pd.notna(ts) else None,
                top_k=top_k,
            )
            results.append(exp)
        return results

    def generate_waterfall_plot(
        self,
        explanation: Dict[str, Any],
        output_path: Union[str, Path],
        max_display: int = 10,
        aggregated: bool = True,
    ) -> Path:
        """
        Generate and save a publication-grade waterfall plot from an explanation result.
        """
        # Reconstruct LocalShapExplainer compatible format if passed full contract
        if "prediction" in explanation and isinstance(explanation["prediction"], dict):
            local_compat = {
                "prediction": explanation["prediction"]["label"],
                "attack_probability": explanation["prediction"]["attack_probability"],
                "normal_probability": explanation["prediction"]["normal_probability"],
                "raw_margin": explanation["prediction"]["raw_margin"],
                "base_value": explanation["explanation"]["base_value"],
                "all_contributions_32": explanation["explanation"]["all_contributions_32"],
            }
        else:
            local_compat = explanation

        return self.local_explainer.generate_waterfall_plot(
            explanation=local_compat,
            output_path=output_path,
            max_display=max_display,
            aggregated=aggregated,
        )
