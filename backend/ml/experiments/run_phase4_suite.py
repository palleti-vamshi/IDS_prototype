"""
Phase 4 Master Experiment Suite

Executes the complete experimental battery required for Phase 4:
1. Experiment 1: Baseline Random Stratified 80/10/10 on authoritative 100K dataset
2. Experiment 2: Chronological / Temporal Evaluation on 100K dataset
3. Experiment 3: Feature Ablation (Without sensor_code)
4. Experiment 4: Feature Ablation (Without physical identity: device_id, sensor_code, topic)

Outputs all standard reports, metrics, curves, confusion matrices, and error breakdowns.
"""

import logging
from pathlib import Path
import time
import pandas as pd

from backend.ml.config import (
    LIGHTX_100K,
    REPORT_DIR,
)
from backend.ml.experiments.experiment import run_benchmark

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_phase4_suite():
    print("=" * 110)
    print("🚀 STARTING LIGHTX-IDS PHASE 4 COMPREHENSIVE EXPERIMENT BATTERY")
    print(f"Authoritative Dataset: {LIGHTX_100K}")
    print("=" * 110)

    start_suite_time = time.time()
    all_results = []

    # -------------------------------------------------------------
    # EXPERIMENT 1: Historical Baseline Features (Stratified 80/10/10)
    # -------------------------------------------------------------
    print("\n" + "#" * 110)
    print("EXPERIMENT 1: HISTORICAL BASELINE FEATURES (Random Stratified 80/10/10)")
    print("#" * 110)
    exp1_results = run_benchmark(
        dataset_path=LIGHTX_100K,
        benchmark_name="benchmark_100k_baseline_features",
        split_protocol="stratified",
        ablation="baseline_features",
    )
    for r in exp1_results:
        r["experiment"] = "Exp 1: Baseline Features (Stratified)"
    all_results.extend(exp1_results)

    # -------------------------------------------------------------
    # EXPERIMENT 2: Ablation — Without Communication Features
    # -------------------------------------------------------------
    print("\n" + "#" * 110)
    print("EXPERIMENT 2: ABLATION — Without Communication Features")
    print("#" * 110)
    exp2_results = run_benchmark(
        dataset_path=LIGHTX_100K,
        benchmark_name="benchmark_100k_ablation_no_comm",
        split_protocol="stratified",
        ablation="no_communication",
    )
    for r in exp2_results:
        r["experiment"] = "Exp 2: Ablation (No Communication)"
    all_results.extend(exp2_results)

    # -------------------------------------------------------------
    # EXPERIMENT 3: Ablation — Without Multi-Window Temporal Features
    # -------------------------------------------------------------
    print("\n" + "#" * 110)
    print("EXPERIMENT 3: ABLATION — Without Multi-Window Temporal Features")
    print("#" * 110)
    exp3_results = run_benchmark(
        dataset_path=LIGHTX_100K,
        benchmark_name="benchmark_100k_ablation_no_multiwindow",
        split_protocol="stratified",
        ablation="no_multiwindow",
    )
    for r in exp3_results:
        r["experiment"] = "Exp 3: Ablation (No Multi-Window)"
    all_results.extend(exp3_results)

    # -------------------------------------------------------------
    # EXPERIMENT 4: Ablation — Without Physical Identity (Pure Physics)
    # -------------------------------------------------------------
    print("\n" + "#" * 110)
    print("EXPERIMENT 4: ABLATION — Without Physical Identity (Pure Behavioral Physics)")
    print("#" * 110)
    exp4_results = run_benchmark(
        dataset_path=LIGHTX_100K,
        benchmark_name="benchmark_100k_ablation_no_identity",
        split_protocol="stratified",
        ablation="no_identity",
    )
    for r in exp4_results:
        r["experiment"] = "Exp 4: Ablation (No Identity)"
    all_results.extend(exp4_results)

    # -------------------------------------------------------------
    # EXPERIMENT 5: Optimized Full Feature Pipeline (Stratified 80/10/10)
    # -------------------------------------------------------------
    print("\n" + "#" * 110)
    print("EXPERIMENT 5: OPTIMIZED FULL PIPELINE (Random Stratified 80/10/10)")
    print("#" * 110)
    exp5_results = run_benchmark(
        dataset_path=LIGHTX_100K,
        benchmark_name="benchmark_100k_optimized_stratified",
        split_protocol="stratified",
        ablation=None,
    )
    for r in exp5_results:
        r["experiment"] = "Exp 5: Optimized Full Pipeline"
    all_results.extend(exp5_results)

    # -------------------------------------------------------------
    # EXPERIMENT 6: Temporal Generalization (Chronological 80/10/10)
    # -------------------------------------------------------------
    print("\n" + "#" * 110)
    print("EXPERIMENT 6: TEMPORAL EVALUATION (Chronological 80/10/10)")
    print("#" * 110)
    exp6_results = run_benchmark(
        dataset_path=LIGHTX_100K,
        benchmark_name="benchmark_100k_temporal",
        split_protocol="temporal",
        ablation=None,
    )
    for r in exp6_results:
        r["experiment"] = "Exp 6: Temporal Generalization"
    all_results.extend(exp6_results)

    # -------------------------------------------------------------
    # COMPILE MASTER COMPARISON TABLE
    # -------------------------------------------------------------
    phase4_reports_dir = Path("reports/phase4")
    phase4_reports_dir.mkdir(parents=True, exist_ok=True)

    master_df = pd.DataFrame(all_results)
    preferred_cols = [
        "experiment",
        "model",
        "split_protocol",
        "ablation",
        "feature_count",
        "best_threshold",
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "pr_auc",
        "fpr",
        "fnr",
        "tp",
        "fp",
        "tn",
        "fn",
        "training_time",
        "prediction_time",
        "model_size_mb",
    ]
    cols_to_use = [c for c in preferred_cols if c in master_df.columns]
    master_df = master_df[cols_to_use]

    master_csv = phase4_reports_dir / "phase4_master_benchmark.csv"
    master_json = phase4_reports_dir / "phase4_master_benchmark.json"

    master_df.to_csv(master_csv, index=False)
    master_df.to_json(master_json, orient="records", indent=4)

    total_duration = time.time() - start_suite_time

    print("\n" + "=" * 110)
    print("🏆 PHASE 4 COMPREHENSIVE EXPERIMENT BATTERY COMPLETE")
    print(f"Total Suite Runtime: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print(f"Master CSV Saved    : {master_csv}")
    print(f"Master JSON Saved   : {master_json}")
    print("=" * 110)

    print("\nMASTER BENCHMARK SUMMARY TABLE:")
    print("-" * 110)
    print(
        master_df[
            [
                "experiment",
                "model",
                "accuracy",
                "precision",
                "recall",
                "f1_score",
                "roc_auc",
                "pr_auc",
                "fpr",
                "fnr",
                "best_threshold",
                "training_time",
            ]
        ].to_string(index=False)
    )

    return master_df


if __name__ == "__main__":
    run_phase4_suite()
