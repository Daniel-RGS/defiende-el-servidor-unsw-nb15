"""Recalcula métricas únicamente desde predicciones-test.csv."""
import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", type=Path)
    args = parser.parse_args()
    data = pd.read_csv(args.predictions)
    y_true = data["y_true"].astype(int)
    y_pred = data["y_pred"].astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    result = {
        "rows": len(data),
        "recall_attack": float(recall_score(y_true, y_pred, zero_division=0)),
        "precision_attack": float(precision_score(y_true, y_pred, zero_division=0)),
        "fpr": float(fp / (fp + tn)) if fp + tn else 0.0,
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "confusion_matrix": cm.tolist(),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
