"""
LightX-IDS Attack-Specific SHAP Explainer

Provides attack-specific SHAP attribution analysis for the frozen Phase 5 H3-32
XGBoost intrusion detection model.

Decomposes predictions across distinct attack classes, aggregates one-hot
features back to original 32 physical input features, evaluates signed and
absolute attributions, and computes cross-attack feature reliance frequencies.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from backend.ml.explainability.shap_local_explainer import (
    LocalShapExplainer,
    ALL_32_FEATURES,
    ACTIVE_NUMERIC_COLUMNS,
    ACTIVE_CATEGORICAL_COLUMNS,
)

logger = logging.getLogger(__name__)

ALL_PHASE2_ATTACKS: List[str] = [
    "DoS Attack",
    "Replay Attack",
    "Packet Delay Attack",
    "Packet Drop Attack",
    "MQTT Topic Hijacking",
    "Sensor Spoofing Attack",
    "False Data Injection Attack",
    "Sensor Drift Attack",
    "Sensor Freeze Attack",
    "Sensor Noise Injection Attack",
    "PLC Command Injection",
    "Unauthorized Command",
    "Setpoint Manipulation",
    "Motor Overload Attack",
    "Valve Stuck Attack",
    "Intermittent Attack",
    "Slow Drift Attack",
]

CONTROL_PLANE_ATTACKS: set = {
    "PLC Command Injection",
    "Unauthorized Command",
    "Setpoint Manipulation",
}

CONTROL_PLANE_REASON: str = (
    "Not available for sensor-level SHAP analysis because Phase 3 intentionally "
    "assigns zero sensor-level labels to this control-plane attack."
)


class AttackSpecificShapExplainer:
    """
    Analyzes attack-specific SHAP attributions across distinct attack categories.
    """

    def __init__(
        self,
        local_explainer: Optional[LocalShapExplainer] = None,
        model_path: Optional[Union[str, Path]] = None,
        threshold: float = 0.35,
    ):
        """
        Initialize the attack-specific explainer.
        """
        if local_explainer is not None:
            self.local_explainer = local_explainer
        else:
            self.local_explainer = LocalShapExplainer(
                model_path=model_path, threshold=threshold
            )

        self.pipeline = self.local_explainer.pipeline
        self.preprocessor = self.local_explainer.preprocessor
        self.classifier = self.local_explainer.classifier
        self.explainer = self.local_explainer.explainer
        self.transformed_names = self.local_explainer.transformed_feature_names
        self.original_to_indices = self.local_explainer.original_to_indices
        self.base_value = self.local_explainer.base_value

    def explain_attack_batch(
        self,
        attack_name: str,
        attack_df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Compute aggregate SHAP attributions for a specific attack type.

        Args:
            attack_name: Name of the attack category.
            attack_df: DataFrame of records belonging to this attack (with 32 H3-32 features).

        Returns:
            Dictionary containing sample count, mean absolute SHAP, mean signed SHAP,
            percentage contributions, and top attack/normal directed contributors.
        """
        sample_count = len(attack_df)
        if sample_count == 0:
            return {
                "attack_type": attack_name,
                "status": "NO_SAMPLES",
                "sample_count": 0,
                "reason": (
                    CONTROL_PLANE_REASON
                    if attack_name in CONTROL_PLANE_ATTACKS
                    else "Zero records in evaluation set."
                ),
            }

        # Select the 32 input features in canonical order
        df_32 = attack_df[ALL_32_FEATURES].copy()

        # Preprocess records into 95-dimensional transformed space
        X_trans = self.preprocessor.transform(df_32)
        X_df = pd.DataFrame(X_trans, columns=self.transformed_names)

        # Compute SHAP values
        shap_explanation = self.explainer(X_df)
        shap_matrix_95 = shap_explanation.values  # Shape: (N, 95)
        raw_margins = self.classifier.predict(X_df, output_margin=True)

        # Aggregate 95-transformed features to 32 original features for every record
        shap_matrix_32 = np.zeros((sample_count, len(ALL_32_FEATURES)))
        for f_idx, feat in enumerate(ALL_32_FEATURES):
            indices = self.original_to_indices[feat]
            if indices:
                shap_matrix_32[:, f_idx] = np.sum(shap_matrix_95[:, indices], axis=1)

        # Compute Mean Absolute SHAP and Mean Signed SHAP
        mean_abs_32 = np.mean(np.abs(shap_matrix_32), axis=0)
        mean_signed_32 = np.mean(shap_matrix_32, axis=0)

        # Total absolute attribution mass for percentage calculation
        total_abs_mass = float(np.sum(mean_abs_32))
        pct_contribs = (
            (mean_abs_32 / total_abs_mass * 100.0) if total_abs_mass > 0 else np.zeros_like(mean_abs_32)
        )

        # Build feature summary table
        features_summary = []
        for f_idx, feat in enumerate(ALL_32_FEATURES):
            feat_type = "Numeric" if feat in ACTIVE_NUMERIC_COLUMNS else "Categorical"
            features_summary.append({
                "feature": feat,
                "feature_type": feat_type,
                "mean_abs_shap": float(mean_abs_32[f_idx]),
                "mean_signed_shap": float(mean_signed_32[f_idx]),
                "percentage_contribution": float(pct_contribs[f_idx]),
            })

        # Sort descending by mean absolute SHAP
        features_summary.sort(key=lambda x: x["mean_abs_shap"], reverse=True)
        for rank, item in enumerate(features_summary, start=1):
            item["rank"] = rank

        # Attack-directed (positive signed SHAP) vs Normal-directed (negative signed SHAP)
        attack_directed = [
            f for f in features_summary if f["mean_signed_shap"] > 0
        ]
        attack_directed.sort(key=lambda x: x["mean_signed_shap"], reverse=True)

        normal_directed = [
            f for f in features_summary if f["mean_signed_shap"] < 0
        ]
        normal_directed.sort(key=lambda x: x["mean_signed_shap"])

        return {
            "attack_type": attack_name,
            "status": "ANALYZED",
            "sample_count": sample_count,
            "mean_abs_shap_32": {f["feature"]: f["mean_abs_shap"] for f in features_summary},
            "mean_signed_shap_32": {f["feature"]: f["mean_signed_shap"] for f in features_summary},
            "top_10_features": features_summary[:10],
            "all_32_features": features_summary,
            "top_attack_directed": attack_directed[:5],
            "top_normal_directed": normal_directed[:5],
            "shap_matrix_32": shap_matrix_32,
            "shap_matrix_95": shap_matrix_95,
            "raw_margins": raw_margins,
            "base_values": shap_explanation.base_values,
        }

    def analyze_all_attacks(
        self,
        test_df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Analyze all known attack categories present in the evaluation split.

        Args:
            test_df: DataFrame containing features, 'label', and 'attack_type'.

        Returns:
            Dictionary mapping attack names to their individual analysis dictionaries,
            plus metadata on coverage and available samples.
        """
        results: Dict[str, Any] = {}
        analyzed_count = 0
        unsupported_count = 0

        for attack_name in ALL_PHASE2_ATTACKS:
            if attack_name in CONTROL_PLANE_ATTACKS:
                results[attack_name] = {
                    "attack_type": attack_name,
                    "status": "CONTROL_PLANE_EXCLUDED",
                    "sample_count": 0,
                    "reason": CONTROL_PLANE_REASON,
                }
                unsupported_count += 1
                continue

            # Filter records where label == 1 and attack_type == attack_name
            subset = test_df[(test_df["label"] == 1) & (test_df["attack_type"] == attack_name)]
            if len(subset) == 0:
                results[attack_name] = {
                    "attack_type": attack_name,
                    "status": "ZERO_SAMPLES",
                    "sample_count": 0,
                    "reason": "No attack-labeled records in evaluation set.",
                }
                unsupported_count += 1
            else:
                logger.info("Analyzing %s (%d records)...", attack_name, len(subset))
                results[attack_name] = self.explain_attack_batch(attack_name, subset)
                analyzed_count += 1

        return {
            "attacks": results,
            "total_attack_types_defined": len(ALL_PHASE2_ATTACKS),
            "analyzed_attack_types": analyzed_count,
            "excluded_attack_types": unsupported_count,
        }

    def verify_fidelity(
        self,
        test_df: pd.DataFrame,
        max_samples: int = 200,
    ) -> Dict[str, Any]:
        """
        Verify additive fidelity across representative attack samples.
        """
        attack_subset = test_df[test_df["label"] == 1]
        n_samples = min(len(attack_subset), max_samples)
        sample_df = attack_subset.iloc[:n_samples].copy()

        df_32 = sample_df[ALL_32_FEATURES].copy()
        X_trans = self.preprocessor.transform(df_32)
        X_df = pd.DataFrame(X_trans, columns=self.transformed_names)

        shap_exp = self.explainer(X_df)
        shap_vals = shap_exp.values
        base_vals = shap_exp.base_values
        raw_margins = self.classifier.predict(X_df, output_margin=True)

        recon_margins = base_vals + np.sum(shap_vals, axis=1)
        errors = np.abs(raw_margins - recon_margins)

        max_err = float(np.max(errors))
        mean_err = float(np.mean(errors))

        return {
            "samples_checked": int(n_samples),
            "max_absolute_error": max_err,
            "mean_absolute_error": mean_err,
            "passes_fidelity": bool(max_err < 1e-4),
        }

    def compute_cross_attack_frequencies(
        self,
        analysis_results: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Compute frequency of appearance in Top 5 and Top 10 across analyzed attacks.
        """
        attacks_data = analysis_results["attacks"]
        analyzed_attacks = [
            a for a, res in attacks_data.items() if res.get("status") == "ANALYZED"
        ]
        num_analyzed = len(analyzed_attacks)

        top5_counts = {f: 0 for f in ALL_32_FEATURES}
        top10_counts = {f: 0 for f in ALL_32_FEATURES}
        mean_abs_sums = {f: 0.0 for f in ALL_32_FEATURES}

        for att in analyzed_attacks:
            top_feats = attacks_data[att]["all_32_features"]
            for rank_idx, item in enumerate(top_feats, start=1):
                f = item["feature"]
                mean_abs_sums[f] += item["mean_abs_shap"]
                if rank_idx <= 5:
                    top5_counts[f] += 1
                if rank_idx <= 10:
                    top10_counts[f] += 1

        records = []
        for f in ALL_32_FEATURES:
            feat_type = "Numeric" if f in ACTIVE_NUMERIC_COLUMNS else "Categorical"
            records.append({
                "feature": f,
                "feature_type": feat_type,
                "top5_count": top5_counts[f],
                "top10_count": top10_counts[f],
                "top5_frequency_pct": round(top5_counts[f] / num_analyzed * 100.0, 1),
                "top10_frequency_pct": round(top10_counts[f] / num_analyzed * 100.0, 1),
                "average_mean_abs_shap": round(mean_abs_sums[f] / num_analyzed, 6),
            })

        df_freq = pd.DataFrame(records)
        df_freq.sort_values(
            by=["top5_count", "top10_count", "average_mean_abs_shap"],
            ascending=False,
            inplace=True,
        )
        df_freq.reset_index(drop=True, inplace=True)
        df_freq["overall_rank"] = np.arange(1, len(df_freq) + 1)
        return df_freq

    def generate_heatmap(
        self,
        analysis_results: Dict[str, Any],
        output_path: Union[str, Path],
        top_n_features: int = 15,
    ) -> Path:
        """
        Generate research-grade heatmap of attack types vs top original features.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        attacks_data = analysis_results["attacks"]
        analyzed_attacks = [
            a for a, res in attacks_data.items() if res.get("status") == "ANALYZED"
        ]

        # Determine overall top N features across all analyzed attacks
        feature_scores = {f: 0.0 for f in ALL_32_FEATURES}
        for att in analyzed_attacks:
            for item in attacks_data[att]["all_32_features"]:
                feature_scores[item["feature"]] += item["mean_abs_shap"]

        sorted_top_feats = sorted(
            feature_scores.keys(), key=lambda f: feature_scores[f], reverse=True
        )[:top_n_features]

        # Build matrix
        matrix = np.zeros((len(analyzed_attacks), len(sorted_top_feats)))
        for row_idx, att in enumerate(analyzed_attacks):
            for col_idx, feat in enumerate(sorted_top_feats):
                matrix[row_idx, col_idx] = attacks_data[att]["mean_abs_shap_32"][feat]

        # Attack labels with sample counts
        row_labels = [
            f"{att} (N={attacks_data[att]['sample_count']})"
            for att in analyzed_attacks
        ]

        fig, ax = plt.subplots(figsize=(14, 10))
        cax = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")

        ax.set_xticks(np.arange(len(sorted_top_feats)))
        ax.set_yticks(np.arange(len(analyzed_attacks)))
        ax.set_xticklabels(sorted_top_feats, rotation=45, ha="right", fontsize=10)
        ax.set_yticklabels(row_labels, fontsize=10)

        # Annotate cell values
        for i in range(len(analyzed_attacks)):
            for j in range(len(sorted_top_feats)):
                val = matrix[i, j]
                color = "white" if val > np.max(matrix) * 0.6 else "black"
                ax.text(
                    j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=8
                )

        cbar = fig.colorbar(cax, ax=ax, fraction=0.03, pad=0.04)
        cbar.set_label("Mean Absolute SHAP Value (Log-Odds Impact)", fontsize=11)

        ax.set_title(
            f"LightX-IDS: Attack-Specific Feature Attribution Heatmap (Top {top_n_features} Features)",
            fontsize=13,
            pad=15,
            fontweight="bold",
        )
        plt.tight_layout()
        plt.savefig(out_p, dpi=300)
        plt.close(fig)
        logger.info("Saved heatmap to %s", out_p)
        return out_p

    def generate_rankings_chart(
        self,
        analysis_results: Dict[str, Any],
        output_path: Union[str, Path],
        top_k: int = 5,
    ) -> Path:
        """
        Generate faceted/multi-panel bar charts displaying top-k features for each attack.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        attacks_data = analysis_results["attacks"]
        analyzed_attacks = [
            a for a, res in attacks_data.items() if res.get("status") == "ANALYZED"
        ]
        n_attacks = len(analyzed_attacks)

        # Grid layout: 4 columns
        cols = 4
        rows = int(np.ceil(n_attacks / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(20, rows * 3.5), sharex=False)
        axes = axes.flatten()

        for idx, att in enumerate(analyzed_attacks):
            ax = axes[idx]
            top_items = attacks_data[att]["top_10_features"][:top_k]
            feats = [x["feature"] for x in top_items][::-1]
            vals = [x["mean_abs_shap"] for x in top_items][::-1]
            types = [x["feature_type"] for x in top_items][::-1]
            colors = ["#2ca02c" if t == "Numeric" else "#ff7f0e" for t in types]

            ax.barh(feats, vals, color=colors, edgecolor="black", linewidth=0.5)
            ax.set_title(
                f"{att} (N={attacks_data[att]['sample_count']})",
                fontsize=10,
                fontweight="bold",
            )
            ax.set_xlabel("Mean |SHAP|", fontsize=8)
            ax.grid(axis="x", linestyle=":", alpha=0.6)
            ax.tick_params(axis="y", labelsize=8)
            ax.tick_params(axis="x", labelsize=8)

        # Hide extra subplots
        for extra_idx in range(n_attacks, len(axes)):
            axes[extra_idx].axis("off")

        # Custom legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor="#2ca02c", edgecolor="black", label="Numeric (Physical / Timing)"),
            Patch(facecolor="#ff7f0e", edgecolor="black", label="Categorical (One-Hot Aggregated)"),
        ]
        fig.legend(handles=legend_elements, loc="upper right", fontsize=11, bbox_to_anchor=(0.98, 0.99))

        fig.suptitle(
            "LightX-IDS: Top 5 Features per Attack Type (H3-32 Frozen Model)",
            fontsize=15,
            fontweight="bold",
            y=1.01,
        )
        plt.tight_layout()
        plt.savefig(out_p, dpi=300, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved rankings chart to %s", out_p)
        return out_p
