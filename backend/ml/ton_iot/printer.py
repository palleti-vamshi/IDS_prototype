"""
TON-IoT Benchmark Printer

Handles all console output for benchmark experiments.
"""

from pathlib import Path


class BenchmarkPrinter:
    """Professional benchmark console printer."""

    LINE = "=" * 110
    SUBLINE = "-" * 110

    MODEL_NAMES = {
        "xgboost": "XGBoost",
        "random_forest": "Random Forest",
        "decision_tree": "Decision Tree",
        "logistic_regression": "Logistic Regression",
    }

    def title(self):

        print()
        print(self.LINE)
        print("TON-IoT MACHINE LEARNING BENCHMARK")
        print(self.LINE)

    def dataset(
        self,
        rows,
        columns,
        train,
        validation,
        test,
    ):

        print("\nDataset Summary")
        print(self.SUBLINE)

        print(f"{'Rows':<22}: {rows:,}")
        print(f"{'Columns':<22}: {columns}")
        print(f"{'Training Samples':<22}: {train:,}")
        print(f"{'Validation Samples':<22}: {validation:,}")
        print(f"{'Testing Samples':<22}: {test:,}")

    def table_header(self):

        print()
        print(self.SUBLINE)

        print(
            f"{'Rank':<6}"
            f"{'Model':<24}"
            f"{'Accuracy':<12}"
            f"{'Precision':<12}"
            f"{'Recall':<12}"
            f"{'F1 Score':<12}"
            f"{'Train(s)':<12}"
            f"{'Size(MB)':<10}"
        )

        print(self.SUBLINE)

    def row(
        self,
        rank,
        row,
    ):

        display_name = self.MODEL_NAMES.get(
            row["model"],
            row["model"],
        )

        print(
            f"{rank:<6}"
            f"{display_name:<24}"
            f"{row['accuracy'] * 100:>8.2f}%   "
            f"{row['precision'] * 100:>8.2f}%   "
            f"{row['recall'] * 100:>8.2f}%   "
            f"{row['f1_score'] * 100:>8.2f}%   "
            f"{row['training_time']:>8.4f}   "
            f"{row['model_size_mb']:>8.3f}"
        )

    def summary(
        self,
        leaderboard,
    ):

        best = max(
            leaderboard,
            key=lambda x: x["accuracy"],
        )

        fastest = min(
            leaderboard,
            key=lambda x: x["training_time"],
        )

        smallest = min(
            leaderboard,
            key=lambda x: x["model_size_mb"],
        )

        best_name = self.MODEL_NAMES.get(
            best["model"],
            best["model"],
        )

        fastest_name = self.MODEL_NAMES.get(
            fastest["model"],
            fastest["model"],
        )

        smallest_name = self.MODEL_NAMES.get(
            smallest["model"],
            smallest["model"],
        )

        print(self.SUBLINE)

        print("\n🏆 SUMMARY")
        print("-" * 40)

        print(
            f"Best Accuracy     : "
            f"{best_name} "
            f"({best['accuracy'] * 100:.2f}%)"
        )

        print(
            f"Fastest Training  : "
            f"{fastest_name} "
            f"({fastest['training_time']:.4f} sec)"
        )

        print(
            f"Smallest Model    : "
            f"{smallest_name} "
            f"({smallest['model_size_mb']:.3f} MB)"
        )

    def reports(
        self,
        csv_file: Path,
        json_file: Path,
    ):

        print("\n📄 Reports")
        print("-" * 40)

        print(f"CSV  : {csv_file}")
        print(f"JSON : {json_file}")

    def models(self):

        print("\n💾 Saved Models")
        print("-" * 40)

        print("backend/ml/saved_models")

    def completed(self):

        print("\n🎉 TON-IoT Benchmark Completed Successfully!")