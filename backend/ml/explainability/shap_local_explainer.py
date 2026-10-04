"""
LightX-IDS Local SHAP Explainer

Provides local per-packet model explanations for the frozen Phase 5 H3-32
XGBoost intrusion detection model.

Decomposes individual predictions into additive feature contributions (SHAP values)
in log-odds margin space and aggregates one-hot categorical features back to their
original 32 physical input features.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.ml.config import (
    MODEL_DIR,
    NUMERIC_COLUMNS,
    CATEGORICAL_COLUMNS,
)

logger = logging.getLogger(__name__)

# Frozen Phase 5 H3-32 ablation
H3_REMOVED = {
    "value_change",
    "abs_value_change",
    "rolling_range_5",
    "rolling_mean_10",
}

ACTIVE_NUMERIC_COLUMNS = [c for c in NUMERIC_COLUMNS if c not in H3_REMOVED]
ACTIVE_CATEGORICAL_COLUMNS = list(CATEGORICAL_COLUMNS)
ALL_32_FEATURES = ACTIVE_NUMERIC_COLUMNS + ACTIVE_CATEGORICAL_COLUMNS


class LocalShapExplainer:
    """
    Reusable Local SHAP Explainer for LightX-IDS.

    Explains individual packet predictions using TreeExplainer in margin space
    and produces aggregated 32-feature contributions.
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        threshold: float = 0.35,
    ):
        """
        Initialize the Local SHAP Explainer.

        Args:
            model_path: Path to the saved model pipeline. Defaults to xgboost_h3_32.pkl.
            threshold: Classification decision threshold for attack classification. Default 0.35.
        """
        if model_path is None:
            self.model_path = MODEL_DIR / "xgboost_h3_32.pkl"
        else:
            self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at: {self.model_path}")

        logger.info("Loading model pipeline from %s", self.model_path)
        self.pipeline = joblib.load(self.model_path)

        if not hasattr(self.pipeline, "named_steps"):
            raise ValueError("Expected an sklearn Pipeline with named_steps.")

        self.preprocessor = self.pipeline.named_steps.get("preprocessor")
        self.classifier = self.pipeline.named_steps.get("classifier")

        if self.preprocessor is None or self.classifier is None:
            raise ValueError("Pipeline must contain 'preprocessor' and 'classifier' steps.")

        self.threshold = float(threshold)
        self.transformed_feature_names = list(self.preprocessor.get_feature_names_out())
        self.num_transformed = len(self.transformed_feature_names)

        # Initialize TreeExplainer
        logger.info("Initializing TreeExplainer on classifier...")
        self.explainer = shap.TreeExplainer(self.classifier)

        # Extract base value
        raw_base = self.explainer.expected_value
        if isinstance(raw_base, (np.ndarray, list)) and len(raw_base) == 1:
            self.base_value = float(raw_base[0])
        else:
            self.base_value = float(raw_base)

        # Build one-hot to original feature mapping
        self._build_feature_mappings()

    def _build_feature_mappings(self) -> None:
        """
        Build mapping from 95 transformed columns back to 32 original input features.
        """
        self.transformed_to_original: Dict[str, str] = {}
        for col in self.transformed_feature_names:
            matched = False
            for cat in ACTIVE_CATEGORICAL_COLUMNS:
                if col.startswith(f"{cat}_"):
                    self.transformed_to_original[col] = cat
                    matched = True
                    break
            if not matched:
                self.transformed_to_original[col] = col

        # Map each original feature to its constituent transformed indices
        self.original_to_indices: Dict[str, List[int]] = {
            f: [] for f in ALL_32_FEATURES
        }
        for idx, col in enumerate(self.transformed_feature_names):
            orig_feat = self.transformed_to_original[col]
            if orig_feat in self.original_to_indices:
                self.original_to_indices[orig_feat].append(idx)

    def explain_instance(
        self,
        observation: Union[Dict[str, Any], pd.Series, pd.DataFrame],
        top_k: int = 5,
        check_fidelity: bool = True,
    ) -> Dict[str, Any]:
        """
        Explain a single observation.

        Args:
            observation: Telemetry observation as dict, Series, or 1-row DataFrame.
            top_k: Number of top positive and negative contributors to return.
            check_fidelity: Whether to assert additive reconstruction fidelity.

        Returns:
            Structured dictionary containing predictions, probabilities, margin,
            base value, and ranked positive/negative feature contributions.
        """
        # Convert observation to 1-row DataFrame
        if isinstance(observation, dict):
            df_inst = pd.DataFrame([observation])
        elif isinstance(observation, pd.Series):
            df_inst = pd.DataFrame([observation.to_dict()])
        elif isinstance(observation, pd.DataFrame):
            if len(observation) != 1:
                raise ValueError(f"Expected 1 observation, got {len(observation)}")
            df_inst = observation.copy()
        else:
            raise TypeError(f"Unsupported observation type: {type(observation)}")

        # Ensure all 32 required features are present
        missing = [f for f in ALL_32_FEATURES if f not in df_inst.columns]
        if missing:
            raise ValueError(f"Observation is missing required H3-32 features: {missing}")

        # Select only the exact 32 features in canonical order
        df_32 = df_inst[ALL_32_FEATURES].copy()

        # Transform through pipeline preprocessor
        X_trans = self.preprocessor.transform(df_32)
        X_df = pd.DataFrame(X_trans, columns=self.transformed_feature_names)

        # Predict raw margin and probabilities
        raw_margin = float(self.classifier.predict(X_df, output_margin=True)[0])
        prob_attack = float(1.0 / (1.0 + np.exp(-raw_margin)))
        prob_normal = float(1.0 - prob_attack)
        prediction = "ATTACK" if prob_attack >= self.threshold else "NORMAL"

        # Compute SHAP values
        shap_explanation = self.explainer(X_df)
        shap_values_95 = shap_explanation.values[0]
        base_val_sample = float(shap_explanation.base_values[0])

        # Fidelity Verification: base_value + sum(SHAP) == margin
        reconstructed_margin = base_val_sample + float(np.sum(shap_values_95))
        fidelity_error = abs(raw_margin - reconstructed_margin)

        if check_fidelity and fidelity_error >= 1e-4:
            raise ValueError(
                f"SHAP additive fidelity failed: margin={raw_margin:.6f}, "
                f"reconstructed={reconstructed_margin:.6f}, error={fidelity_error:.6e}"
            )

        # Aggregate one-hot features to original 32 features
        shap_32: Dict[str, float] = {}
        for feat in ALL_32_FEATURES:
            member_indices = self.original_to_indices[feat]
            if member_indices:
                shap_32[feat] = float(np.sum(shap_values_95[member_indices]))
            else:
                shap_32[feat] = 0.0

        # Separate positive (pushes toward ATTACK) and negative (pushes toward NORMAL)
        positive_contributors = []
        negative_contributors = []

        for feat, val in shap_32.items():
            feat_type = "Numeric" if feat in ACTIVE_NUMERIC_COLUMNS else "Categorical"
            item = {
                "feature": feat,
                "shap_value": val,
                "feature_type": feat_type,
                "raw_value": df_32[feat].iloc[0] if feat in df_32.columns else None,
            }
            if val > 0:
                positive_contributors.append(item)
            elif val < 0:
                negative_contributors.append(item)

        # Sort positive descending (strongest push to attack first)
        positive_contributors.sort(key=lambda x: x["shap_value"], reverse=True)
        # Sort negative ascending (strongest push to normal first, i.e. most negative)
        negative_contributors.sort(key=lambda x: x["shap_value"])

        top_positive = positive_contributors[:top_k]
        top_negative = negative_contributors[:top_k]

        return {
            "prediction": prediction,
            "attack_probability": prob_attack,
            "normal_probability": prob_normal,
            "raw_margin": raw_margin,
            "base_value": base_val_sample,
            "reconstructed_margin": reconstructed_margin,
            "fidelity_error": fidelity_error,
            "threshold": self.threshold,
            "top_positive_contributors": top_positive,
            "top_negative_contributors": top_negative,
            "all_positive_contributors": positive_contributors,
            "all_negative_contributors": negative_contributors,
            "all_contributions_32": dict(
                sorted(shap_32.items(), key=lambda item: abs(item[1]), reverse=True)
            ),
            "shap_values_95": dict(zip(self.transformed_feature_names, shap_values_95)),
            "raw_features": df_32.iloc[0].to_dict(),
            "explanation_object": shap_explanation,
        }

    def generate_waterfall_plot(
        self,
        explanation: Dict[str, Any],
        output_path: Union[str, Path],
        max_display: int = 10,
        title: Optional[str] = None,
        aggregated: bool = True,
    ) -> Path:
        """
        Generate a publication-grade waterfall plot for a local explanation.

        Args:
            explanation: Result dictionary from explain_instance.
            output_path: Path where the plot image should be saved.
            max_display: Maximum number of features to display.
            title: Custom title for the plot.
            aggregated: If True, plots aggregated 32-space features; if False, plots 95-space.

        Returns:
            Path to saved plot file.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        pred = explanation["prediction"]
        p_att = explanation["attack_probability"] * 100.0
        margin = explanation["raw_margin"]
        base = explanation["base_value"]

        if aggregated:
            # Create a clean custom aggregated waterfall plot for the 32 features
            contribs = explanation["all_contributions_32"]
            sorted_feats = list(contribs.keys())[:max_display]
            sorted_vals = [contribs[f] for f in sorted_feats]

            # Invert for horizontal bar layout (top feature at top)
            sorted_feats = sorted_feats[::-1]
            sorted_vals = sorted_vals[::-1]

            fig, ax = plt.subplots(figsize=(10, max(5, int(max_display * 0.45))))
            colors = ["#e74c3c" if v > 0 else "#3498db" for v in sorted_vals]
            bars = ax.barh(sorted_feats, sorted_vals, color=colors, edgecolor="black", linewidth=0.6)

            # Draw vertical baseline at zero
            ax.axvline(0, color="gray", linestyle="--", alpha=0.7)

            # Value labels on bars
            for bar, val in zip(bars, sorted_vals):
                width = bar.get_width()
                offset = 0.05 if val >= 0 else -0.05
                align = "left" if val >= 0 else "right"
                ax.text(
                    width + offset,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:+.3f}",
                    va="center",
                    ha=align,
                    fontsize=9,
                    fontweight="bold",
                )

            if title is None:
                title = f"Local Explanation | Pred: {pred} (P(Attack)={p_att:.1f}%) | Margin: {margin:+.2f} (Base: {base:+.2f})"
            ax.set_title(title, fontsize=12, pad=12, fontweight="bold")
            ax.set_xlabel("SHAP Value (Log-Odds Impact on Model Margin)", fontsize=11)
            ax.grid(axis="x", linestyle=":", alpha=0.5)

            # Custom legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor="#e74c3c", edgecolor="black", label="Pushes toward ATTACK (+)"),
                Patch(facecolor="#3498db", edgecolor="black", label="Pushes toward NORMAL (−)"),
            ]
            ax.legend(handles=legend_elements, loc="lower right", fontsize=10)

            plt.tight_layout()
            plt.savefig(out_p, dpi=300)
            plt.close(fig)
        else:
            # Use SHAP standard waterfall on 95 transformed features
            fig = plt.figure(figsize=(10, 8))
            shap.plots.waterfall(
                explanation["explanation_object"][0],
                max_display=max_display,
                show=False,
            )
            if title is None:
                title = f"SHAP Waterfall (Transformed 95) | Pred: {pred} (P(Attack)={p_att:.1f}%)"
            plt.title(title, fontsize=12, pad=15)
            plt.tight_layout()
            plt.savefig(out_p, dpi=300)
            plt.close(fig)

        logger.info("Saved local explanation plot to %s", out_p)
        return out_p
