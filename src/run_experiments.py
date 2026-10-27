import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from .config import EXCLUDED, EXPERIMENT_NAME, RAW_TRAIN, SEED, SPLITS
from .metrics import binary_metrics
from .pipeline import make_pipeline, save_pipeline

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidencias"
MODEL_OUT = OUT / "modelos"

SPECS = [
    ("logistic_baseline", "logistic_regression", "Referencia logística regularizada interpretable.", LogisticRegression, {"max_iter": 1000, "C": 1.0}),
    ("logistic_balanced", "logistic_regression", "class_weight=balanced aumenta recall a costa de FPR.", LogisticRegression, {"max_iter": 1000, "C": 1.0, "class_weight": "balanced"}),
    ("logistic_regularization", "logistic_regression", "C=0.1 aumenta regularización y puede mejorar macro-F1.", LogisticRegression, {"max_iter": 1000, "C": 0.1}),
    ("tree_baseline", "decision_tree", "Un árbol captura relaciones no lineales.", DecisionTreeClassifier, {"random_state": SEED, "max_depth": 12}),
    ("tree_balanced", "decision_tree", "class_weight=balanced mejora recall en el árbol.", DecisionTreeClassifier, {"random_state": SEED, "max_depth": 12, "class_weight": "balanced"}),
    ("random_forest", "random_forest", "Un bosque reduce la varianza y mejora macro-F1.", RandomForestClassifier, {"n_estimators": 100, "max_depth": 18, "random_state": SEED, "n_jobs": -1, "class_weight": "balanced"}),
]

def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"

def main():
    OUT.mkdir(exist_ok=True); MODEL_OUT.mkdir(exist_ok=True)
    data = pd.read_csv(RAW_TRAIN)
    assignment = pd.read_csv(SPLITS)
    X = data.drop(columns=EXCLUDED); y = data["label"]
    train = assignment["split"].eq("train"); valid = assignment["split"].eq("validation")
    X_train, y_train, X_valid, y_valid = X[train], y[train], X[valid], y[valid]
    mlflow.set_experiment(EXPERIMENT_NAME)
    rows = []
    for run_id, family, hypothesis, cls, params in SPECS:
        with mlflow.start_run(run_name=run_id) as run:
            model = make_pipeline(X_train, cls(**params))
            model.fit(X_train, y_train)
            score = model.predict_proba(X_valid)[:, 1]
            metrics = binary_metrics(y_valid, score, 0.5)
            mlflow.log_params({**params, "seed": SEED, "data_version": "train+fixed-splits", "git_commit": git_commit(), "hypothesis": hypothesis})
            mlflow.log_metrics({k: v for k, v in metrics.items() if k != "confusion_matrix"})
            mlflow.log_dict({"confusion_matrix": metrics["confusion_matrix"]}, "confusion_matrix.json")
            artifact = MODEL_OUT / f"{run_id}.joblib"; save_pipeline(model, artifact); mlflow.log_artifact(str(artifact))
            row = {"id": run_id, "family": family, "hypothesis": hypothesis, "run_id": run.info.run_id, "seed": SEED, "git_commit": git_commit(), "dvc_version": "data/prepared.dvc", **metrics}
            rows.append(row)
            # Persist each run immediately, not only after the batch.
            pd.DataFrame(rows).to_csv(OUT / "experimentos.csv", index=False)
            (OUT / f"{run_id}.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
            print(json.dumps(row, ensure_ascii=False))

if __name__ == "__main__": main()
