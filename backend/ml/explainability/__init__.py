"""
LightX-IDS Explainability Package

Provides model explainability modules using SHAP (SHapley Additive exPlanations)
for the LightX-IDS Industrial IoT Intrusion Detection System.
"""

from backend.ml.explainability.shap_local_explainer import LocalShapExplainer
from backend.ml.explainability.attack_explainer import AttackSpecificShapExplainer
from backend.ml.explainability.human_explainer import HumanReadableExplainer
from backend.ml.explainability.service import ExplainabilityService

__all__ = [
    "LocalShapExplainer",
    "AttackSpecificShapExplainer",
    "HumanReadableExplainer",
    "ExplainabilityService",
]
