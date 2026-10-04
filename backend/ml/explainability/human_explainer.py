"""
LightX-IDS Human-Readable Explainer

Converts numerical SHAP explanation values produced by LocalShapExplainer and
AttackSpecificShapExplainer into concise, scientifically defensible, human-readable
interpretations for Industrial IoT (IIoT) control room operators.

Important Scientific & Safety Principles:
- SHAP explains MODEL DECISION BEHAVIOR, not physical causality.
- Probabilities reflect model assignment, not real-world certainty guarantees.
- Operator guidance is strictly investigatory/advisory; no unsafe physical commands
  (e.g., shutdown, disconnect) are ever issued.
- Ground-truth attack categories are clearly distinguished from model inferences.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.ml.explainability.shap_local_explainer import (
    LocalShapExplainer,
    ALL_32_FEATURES,
    ACTIVE_NUMERIC_COLUMNS,
    ACTIVE_CATEGORICAL_COLUMNS,
)

logger = logging.getLogger(__name__)

# Controlled human-readable feature descriptions for all 32 H3-32 features
FEATURE_DESCRIPTIONS: Dict[str, str] = {
    # 25 Numeric Features
    "value": "current sensor value",
    "value_accel": "sensor value acceleration",
    "time_delta": "current inter-arrival time",
    "rolling_time_delta_5": "recent inter-arrival timing pattern",
    "rolling_time_delta_std_5": "recent timing variability",
    "is_negative_time_delta": "negative timestamp anomaly indicator",
    "global_time_delta": "network-wide inter-arrival time",
    "rolling_global_td_10": "recent network-wide inter-arrival pattern",
    "rolling_global_td_std_10": "recent network-wide timing variability",
    "packet_rate_10": "recent packet rate",
    "is_duplicate_value": "immediate duplicate value indicator",
    "device_seq_gap": "sequence number gap",
    "seq_gap_dev": "sequence gap deviation",
    "rolling_seq_std_5": "sequence number jitter",
    "rolling_mean_3": "short-term rolling mean",
    "rolling_std_3": "short-term value variability",
    "rolling_mean_5": "medium-term rolling mean",
    "rolling_std_5": "medium-term value variability",
    "rolling_std_10": "recent value variability",
    "plant_duplicate_ratio_19": "plant-wide duplicate-value ratio",
    "percentage_change": "recent percentage change in sensor value",
    "device_mean_deviation": "deviation from device historical mean",
    "z_score": "statistical z-score relative to baseline",
    "rel_volatility": "relative value volatility",
    "stability_anomaly": "sensor stability anomaly score",
    # 7 Categorical Features
    "topic": "MQTT topic identity",
    "device_id": "device identity",
    "sensor_code": "sensor identity code",
    "sensor_type": "sensor type",
    "unit": "measurement unit",
    "status": "sensor status",
    "source": "telemetry source",
}

# Scientific & Operational Limitations
EXPLANATION_LIMITATIONS: List[str] = [
    "SHAP explains model decision behavior and feature attribution, not physical causality.",
    "Confidence categories are qualitative communication labels, not calibrated statistical probability guarantees.",
    "The model's explanation does not independently infer or verify the ground-truth attack category.",
    "Operator recommendations are advisory; all operational actions must be verified against physical systems and plant safety protocols.",
]


class HumanReadableExplainer:
    """
    Translates numerical SHAP explanations into structured and narrative human-readable text.
    """

    def __init__(
        self,
        local_explainer: Optional[LocalShapExplainer] = None,
        feature_descriptions: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize HumanReadableExplainer.

        Args:
            local_explainer: Optional instance of LocalShapExplainer.
            feature_descriptions: Optional custom dictionary mapping feature names to descriptions.
        """
        self.local_explainer = local_explainer
        self.feature_descriptions = dict(FEATURE_DESCRIPTIONS)
        if feature_descriptions:
            self.feature_descriptions.update(feature_descriptions)

    def describe_feature(self, feature_name: str) -> str:
        """
        Lookup human-readable description for a feature.
        """
        if feature_name in self.feature_descriptions:
            return self.feature_descriptions[feature_name]
        # Graceful fallback for unknown feature names
        return feature_name.replace("_", " ")

    @staticmethod
    def get_confidence_category(attack_probability: float) -> str:
        """
        Map model-assigned probability to a controlled communication category.
        """
        p = float(attack_probability)
        if p >= 0.90:
            return "high model confidence"
        elif p >= 0.70:
            return "moderate-to-high model confidence"
        elif p >= 0.50:
            return "moderate model confidence"
        elif p >= 0.30:
            return "moderate evidence toward Normal"
        else:
            return "low attack probability"

    @staticmethod
    def get_contribution_strength(shap_value: float) -> Tuple[str, str]:
        """
        Classify the relative strength of a SHAP contribution based on magnitude.

        Returns:
            Tuple of (adjective, adverb), e.g. ('very strong', 'very strongly').
        """
        mag = abs(float(shap_value))
        if mag >= 2.0:
            return "very strong", "very strongly"
        elif mag >= 1.0:
            return "strong", "strongly"
        elif mag >= 0.3:
            return "moderate", "moderately"
        else:
            return "weak", "slightly"

    def explain(
        self,
        local_explanation: Dict[str, Any],
        attack_type: Optional[str] = None,
        record_id: Optional[Union[int, str]] = None,
    ) -> Dict[str, Any]:
        """
        Convert a local SHAP explanation dictionary into human-readable structured output.

        Args:
            local_explanation: Output dictionary from LocalShapExplainer.explain_instance.
            attack_type: Optional ground-truth recorded attack category.
            record_id: Optional record identifier.

        Returns:
            Structured dictionary containing narrative summary, ranked feature sentences,
            operator guidance, and limitation disclosures.
        """
        prediction = str(local_explanation.get("prediction", "UNKNOWN")).upper()
        p_attack = float(local_explanation.get("attack_probability", 0.0))
        p_normal = float(local_explanation.get("normal_probability", 1.0 - p_attack))
        raw_margin = float(local_explanation.get("raw_margin", 0.0))
        base_value = float(local_explanation.get("base_value", 0.0))

        rec_id = record_id if record_id is not None else local_explanation.get("record_id")
        confidence_category = self.get_confidence_category(p_attack)
        is_borderline = bool(0.30 <= p_attack <= 0.70)

        # Ground-truth attack type handling
        # Ground-truth attack type handling
        rec_attack_type = attack_type if attack_type is not None else local_explanation.get("attack_type")
        is_missing = (
            rec_attack_type is None
            or str(rec_attack_type).strip().lower() in ("none", "nan", "null", "")
        )
        if not is_missing:
            gt_text = f"The dataset records this sample as {rec_attack_type}."
            att_type_str = str(rec_attack_type)
        else:
            gt_text = "Recorded attack type: not provided."
            att_type_str = "not provided"

        # Extract top contributors
        pos_raw = local_explanation.get("top_positive_contributors", [])
        neg_raw = local_explanation.get("top_negative_contributors", [])

        top_attack_contributors = []
        for item in pos_raw:
            feat = item["feature"]
            val = float(item["shap_value"])
            desc = self.describe_feature(feat)
            adj, adv = self.get_contribution_strength(val)
            top_attack_contributors.append({
                "feature": feat,
                "description": desc,
                "shap_value": val,
                "strength": adj,
                "direction": "attack",
                "raw_value": item.get("raw_value"),
                "sentence": (
                    f"The {desc} contributed {adv} toward the Attack prediction "
                    f"(SHAP: {val:+.4f})."
                ),
            })

        top_normal_contributors = []
        for item in neg_raw:
            feat = item["feature"]
            val = float(item["shap_value"])
            desc = self.describe_feature(feat)
            adj, adv = self.get_contribution_strength(val)
            top_normal_contributors.append({
                "feature": feat,
                "description": desc,
                "shap_value": val,
                "strength": adj,
                "direction": "normal",
                "raw_value": item.get("raw_value"),
                "sentence": (
                    f"The {desc} contributed {adv} toward the Normal prediction "
                    f"(SHAP: {val:+.4f})."
                ),
            })

        # Generate 2-4 sentence human-readable summary
        summary = self._generate_summary(
            prediction=prediction,
            p_attack=p_attack,
            confidence_category=confidence_category,
            is_borderline=is_borderline,
            top_attack=top_attack_contributors,
            top_normal=top_normal_contributors,
        )

        # Generate operator interpretation
        operator_interpretation = self._generate_operator_interpretation(
            prediction=prediction,
            is_borderline=is_borderline,
            top_attack=top_attack_contributors,
            top_normal=top_normal_contributors,
        )

        structured_output = {
            "record_id": rec_id,
            "prediction": prediction,
            "attack_probability": p_attack,
            "normal_probability": p_normal,
            "confidence_category": confidence_category,
            "is_borderline": is_borderline,
            "attack_type": att_type_str,
            "ground_truth_context": gt_text,
            "raw_margin": raw_margin,
            "base_value": base_value,
            "summary": summary,
            "top_attack_contributors": top_attack_contributors,
            "top_normal_contributors": top_normal_contributors,
            "operator_interpretation": operator_interpretation,
            "limitations": list(EXPLANATION_LIMITATIONS),
        }

        # Formatted narrative text block
        structured_output["text"] = self.to_text(structured_output)
        return structured_output

    def explain_instance(
        self,
        observation: Any,
        attack_type: Optional[str] = None,
        record_id: Optional[Union[int, str]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Explain a raw observation directly by delegating to LocalShapExplainer first.
        """
        if self.local_explainer is None:
            raise ValueError(
                "LocalShapExplainer instance required to call explain_instance. "
                "Initialize HumanReadableExplainer with local_explainer or call explain() "
                "with pre-computed explanation."
            )
        local_res = self.local_explainer.explain_instance(observation, top_k=top_k)
        return self.explain(local_res, attack_type=attack_type, record_id=record_id)

    def _generate_summary(
        self,
        prediction: str,
        p_attack: float,
        confidence_category: str,
        is_borderline: bool,
        top_attack: List[Dict[str, Any]],
        top_normal: List[Dict[str, Any]],
    ) -> str:
        """
        Build concise 2-4 sentence narrative summary.
        """
        pct = p_attack * 100.0

        if is_borderline:
            attack_drivers = [f["description"] for f in top_attack[:2]]
            normal_drivers = [f["description"] for f in top_normal[:2]]
            d_att_str = " and ".join(attack_drivers) if attack_drivers else "timing behavior"
            d_norm_str = " and ".join(normal_drivers) if normal_drivers else "baseline stability"

            return (
                f"The model's prediction is relatively uncertain (assigned attack probability: {pct:.2f}%, "
                f"{confidence_category}), with evidence distributed between Attack and Normal. "
                f"While {d_att_str} provided evidence toward Attack, {d_norm_str} contributed toward Normal. "
                f"The final prediction is {prediction} based on the decision threshold."
            )

        if prediction == "ATTACK":
            primary = [f["description"] for f in top_attack[:2]]
            d_str = " and ".join(primary) if primary else "telemetry timing behavior"
            opp_str = ""
            if top_normal:
                opp_str = f", while {top_normal[0]['description']} contributed toward the Normal side"

            return (
                f"Attack detected with a {pct:.2f}% model-assigned attack probability ({confidence_category}). "
                f"The prediction was driven primarily by {d_str}. "
                f"These features contributed strongly toward the Attack prediction{opp_str}."
            )
        else:
            primary = [f["description"] for f in top_normal[:2]]
            d_str = " and ".join(primary) if primary else "nominal telemetry patterns"
            opp_str = ""
            if top_attack:
                opp_str = f"Minor evidence toward Attack came from {top_attack[0]['description']}, but was outweighed by normal indications."
            else:
                opp_str = "No strong attack-directed contribution was observed in this sample."

            return (
                f"The model assigned a {pct:.2f}% attack probability ({confidence_category}) and predicted Normal. "
                f"The strongest contributions pushed toward the Normal class, particularly {d_str}. "
                f"{opp_str}"
            )

    def _generate_operator_interpretation(
        self,
        prediction: str,
        is_borderline: bool,
        top_attack: List[Dict[str, Any]],
        top_normal: List[Dict[str, Any]],
    ) -> str:
        """
        Build actionable, advisory operator interpretation without unsafe operational commands.
        """
        if is_borderline:
            return (
                "Operator interpretation: Telemetry exhibits borderline characteristics with conflicting "
                "evidence between attack and normal patterns. Monitor subsequent packets on this telemetry "
                "stream for persistent anomalies before initiating operational investigations."
            )

        if prediction == "ATTACK":
            drivers = [f["description"] for f in top_attack[:2]]
            d_str = " and ".join(drivers) if drivers else "cadence and physical telemetry behavior"
            return (
                f"Operator interpretation: The model detected an abnormal telemetry pattern characterized "
                f"by {d_str}. Review the affected telemetry stream and recent communication behavior; "
                f"verify physical sensor readings and correlate with plant logs."
            )
        else:
            return (
                "Operator interpretation: Telemetry patterns fall within nominal operating boundaries. "
                "The model did not detect an anomalous pattern in this sample. Standard monitoring continues."
            )

    def to_text(self, exp: Dict[str, Any]) -> str:
        """
        Format structured explanation into a clean, human-readable text document.
        """
        rec_header = f"RECORD #{exp['record_id']} | " if exp.get("record_id") is not None else ""
        lines = [
            "=" * 78,
            f"LIGHTX-IDS EXPLANATION | {rec_header}PREDICTION: {exp['prediction']}",
            "=" * 78,
            f"Assigned Attack Probability : {exp['attack_probability'] * 100.0:.2f}% ({exp['confidence_category']})",
            f"Model Margin (Base Value)   : {exp['raw_margin']:+.4f} (Base: {exp['base_value']:+.4f})",
            f"Recorded Context            : {exp['ground_truth_context']}",
            "",
            "SUMMARY:",
            f"  {exp['summary']}",
            "",
            "KEY ATTACK-DIRECTED CONTRIBUTORS (+):",
        ]

        if exp["top_attack_contributors"]:
            for idx, c in enumerate(exp["top_attack_contributors"], start=1):
                raw_info = f" [Raw: {c['raw_value']}]" if c.get("raw_value") is not None else ""
                lines.append(
                    f"  {idx}. {c['description']} ({c['feature']}){raw_info}"
                )
                lines.append(f"     SHAP Impact: {c['shap_value']:+.4f} ({c['strength']})")
        else:
            lines.append("  (None observed)")

        lines.extend([
            "",
            "KEY NORMAL-DIRECTED CONTRIBUTORS (-):",
        ])

        if exp["top_normal_contributors"]:
            for idx, c in enumerate(exp["top_normal_contributors"], start=1):
                raw_info = f" [Raw: {c['raw_value']}]" if c.get("raw_value") is not None else ""
                lines.append(
                    f"  {idx}. {c['description']} ({c['feature']}){raw_info}"
                )
                lines.append(f"     SHAP Impact: {c['shap_value']:+.4f} ({c['strength']})")
        else:
            lines.append("  (None observed)")

        lines.extend([
            "",
            "OPERATOR GUIDANCE:",
            f"  {exp['operator_interpretation']}",
            "",
            "SCIENTIFIC & OPERATIONAL LIMITATIONS:",
        ])
        for lim in exp["limitations"]:
            lines.append(f"  • {lim}")

        lines.append("=" * 78)
        return "\n".join(lines)
