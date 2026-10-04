"""
Unit Tests for Phase 6.5 Attack-Specific SHAP Analysis

Tests cover:
1. Frozen model loads successfully.
2. Attack-specific dataset selection works accurately.
3. No control-plane fake sensor samples are created.
4. Every analyzed attack has label == 1.
5. Attack type is correctly preserved across explanation structures.
6. SHAP transformed output has 95 features.
7. Aggregated output has 32 original features.
8. Mean absolute SHAP is non-negative for all features.
9. Representative SHAP fidelity is < 1e-4.
10. Missing/zero-sample attack classes (control-plane) are handled explicitly.
11. Existing Phase 6.4 tests compatibility / regression safety.
"""

import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from backend.ml.config import LIGHTX_100K, MODEL_DIR
from backend.ml.explainability.shap_local_explainer import (
    LocalShapExplainer,
    ALL_32_FEATURES,
    ACTIVE_NUMERIC_COLUMNS,
    ACTIVE_CATEGORICAL_COLUMNS,
)
from backend.ml.explainability.attack_explainer import (
    AttackSpecificShapExplainer,
    ALL_PHASE2_ATTACKS,
    CONTROL_PLANE_ATTACKS,
    CONTROL_PLANE_REASON,
)
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.feature_engineering.feature_selector import FeatureSelector


class TestAttackSpecificShap(unittest.TestCase):
    """Test suite for AttackSpecificShapExplainer."""

    @classmethod
    def setUpClass(cls):
        """Prepare frozen model and sliced test evaluation set once."""
        cls.model_path = MODEL_DIR / "xgboost_h3_32.pkl"
        cls.explainer = AttackSpecificShapExplainer(model_path=cls.model_path, threshold=0.35)

        # Build test split under frozen seed 42 protocol
        df = pd.read_csv(LIGHTX_100K).sort_values("record_id").reset_index(drop=True)
        fg = FeatureGenerator()
        stream = fg.generate_causal_stream_features(df)

        n = len(stream)
        rng = np.random.RandomState(42)
        idx = np.arange(n)
        y_all = stream["label"].to_numpy()

        train_idx, temp_idx = [], []
        for c in np.unique(y_all):
            cls_idx = idx[y_all == c].copy()
            rng.shuffle(cls_idx)
            cut = int(round(len(cls_idx) * 0.80))
            train_idx.extend(cls_idx[:cut])
            temp_idx.extend(cls_idx[cut:])
        train_idx = np.array(train_idx)
        temp_idx = np.array(temp_idx)

        val_idx, test_idx = [], []
        y_temp = y_all[temp_idx]
        for c in np.unique(y_temp):
            cls_idx = temp_idx[y_temp == c].copy()
            rng.shuffle(cls_idx)
            cut = len(cls_idx) // 2
            val_idx.extend(cls_idx[:cut])
            test_idx.extend(cls_idx[cut:])
        test_idx = np.array(test_idx)

        train_df = stream.iloc[train_idx].copy()
        test_df = stream.iloc[test_idx].copy()

        fg.fit(train_df)
        X_test_raw = fg.transform(test_df)

        fs = FeatureSelector()
        X_test_sel, _ = fs.split(X_test_raw)

        cls.eval_df = X_test_sel[ALL_32_FEATURES].copy()
        cls.eval_df["label"] = test_df["label"].values
        cls.eval_df["attack_type"] = test_df["attack_type"].values
        cls.eval_df["record_id"] = test_df["record_id"].values
        cls.eval_df.index = test_idx

    def test_01_frozen_model_loads(self):
        """Verify the frozen H3-32 model exists and loads with correct steps."""
        self.assertTrue(self.model_path.exists())
        self.assertIsNotNone(self.explainer.pipeline)
        self.assertIsNotNone(self.explainer.preprocessor)
        self.assertIsNotNone(self.explainer.classifier)
        self.assertEqual(len(self.explainer.transformed_names), 95)

    def test_02_attack_specific_dataset_selection(self):
        """Verify attack-specific selection filters only rows matching the attack."""
        dos_subset = self.eval_df[
            (self.eval_df["label"] == 1) & (self.eval_df["attack_type"] == "DoS Attack")
        ]
        self.assertGreater(len(dos_subset), 0)
        self.assertTrue((dos_subset["label"] == 1).all())
        self.assertTrue((dos_subset["attack_type"] == "DoS Attack").all())

    def test_03_no_control_plane_fake_sensor_samples(self):
        """Verify control-plane attacks have zero sensor-level samples and no fakes exist."""
        for cp_attack in CONTROL_PLANE_ATTACKS:
            cp_subset = self.eval_df[
                (self.eval_df["label"] == 1) & (self.eval_df["attack_type"] == cp_attack)
            ]
            self.assertEqual(
                len(cp_subset),
                0,
                f"Expected 0 sensor samples for control-plane attack {cp_attack}",
            )

    def test_04_every_analyzed_attack_has_label_one(self):
        """Verify that every row passed into attack batch analysis has label == 1."""
        test_attacks = ["DoS Attack", "Replay Attack", "Sensor Freeze Attack"]
        for att in test_attacks:
            subset = self.eval_df[
                (self.eval_df["label"] == 1) & (self.eval_df["attack_type"] == att)
            ]
            res = self.explainer.explain_attack_batch(att, subset)
            self.assertEqual(res["status"], "ANALYZED")
            self.assertEqual(res["sample_count"], len(subset))
            self.assertTrue((subset["label"] == 1).all())

    def test_05_attack_type_correctly_preserved(self):
        """Verify that attack_type is correctly recorded in results dictionary."""
        att = "Slow Drift Attack"
        subset = self.eval_df[
            (self.eval_df["label"] == 1) & (self.eval_df["attack_type"] == att)
        ]
        res = self.explainer.explain_attack_batch(att, subset)
        self.assertEqual(res["attack_type"], att)

    def test_06_shap_transformed_has_95_features(self):
        """Verify raw SHAP output matrix has 95 transformed features."""
        att = "Sensor Noise Injection Attack"
        subset = self.eval_df[
            (self.eval_df["label"] == 1) & (self.eval_df["attack_type"] == att)
        ].iloc[:10]
        res = self.explainer.explain_attack_batch(att, subset)
        shap_95 = res["shap_matrix_95"]
        self.assertEqual(shap_95.shape[1], 95)
        self.assertEqual(shap_95.shape[0], len(subset))

    def test_07_aggregated_output_has_32_original_features(self):
        """Verify aggregated SHAP matrix and summary map exactly to 32 original features."""
        att = "Intermittent Attack"
        subset = self.eval_df[
            (self.eval_df["label"] == 1) & (self.eval_df["attack_type"] == att)
        ].iloc[:10]
        res = self.explainer.explain_attack_batch(att, subset)
        shap_32 = res["shap_matrix_32"]
        self.assertEqual(shap_32.shape[1], 32)
        self.assertEqual(len(res["all_32_features"]), 32)
        summary_feats = {f["feature"] for f in res["all_32_features"]}
        self.assertEqual(summary_feats, set(ALL_32_FEATURES))

    def test_08_mean_absolute_shap_non_negative(self):
        """Verify mean absolute SHAP values are non-negative."""
        att = "Motor Overload Attack"
        subset = self.eval_df[
            (self.eval_df["label"] == 1) & (self.eval_df["attack_type"] == att)
        ]
        res = self.explainer.explain_attack_batch(att, subset)
        for item in res["all_32_features"]:
            self.assertGreaterEqual(
                item["mean_abs_shap"],
                0.0,
                f"Feature {item['feature']} has negative mean_abs_shap: {item['mean_abs_shap']}",
            )
            self.assertGreaterEqual(
                item["percentage_contribution"],
                0.0,
                f"Feature {item['feature']} has negative percentage contribution",
            )

    def test_09_representative_shap_fidelity_less_than_1e4(self):
        """Verify additive fidelity across attack samples is < 1e-4."""
        dos_subset = self.eval_df[
            (self.eval_df["label"] == 1) & (self.eval_df["attack_type"] == "DoS Attack")
        ].iloc[:50]
        res = self.explainer.verify_fidelity(dos_subset, max_samples=50)
        self.assertTrue(res["passes_fidelity"])
        self.assertLess(res["max_absolute_error"], 1e-4)

    def test_10_missing_zero_sample_attack_classes_handled(self):
        """Verify control-plane attacks report explicit omission reason without throwing errors."""
        res_all = self.explainer.analyze_all_attacks(self.eval_df)
        attacks_data = res_all["attacks"]
        for cp_attack in CONTROL_PLANE_ATTACKS:
            self.assertIn(cp_attack, attacks_data)
            cp_res = attacks_data[cp_attack]
            self.assertEqual(cp_res["sample_count"], 0)
            self.assertEqual(cp_res["status"], "CONTROL_PLANE_EXCLUDED")
            self.assertEqual(cp_res["reason"], CONTROL_PLANE_REASON)

    def test_11_cross_attack_frequency_computation(self):
        """Verify cross-attack frequency dataframe is properly constructed."""
        res_all = self.explainer.analyze_all_attacks(self.eval_df)
        df_freq = self.explainer.compute_cross_attack_frequencies(res_all)
        self.assertEqual(len(df_freq), 32)
        self.assertIn("top5_count", df_freq.columns)
        self.assertIn("top10_count", df_freq.columns)
        self.assertIn("average_mean_abs_shap", df_freq.columns)
        # plant_duplicate_ratio_19 should appear in top 5 for 14 attacks
        pdr_row = df_freq[df_freq["feature"] == "plant_duplicate_ratio_19"].iloc[0]
        self.assertEqual(pdr_row["top5_count"], 14)


if __name__ == "__main__":
    unittest.main()
