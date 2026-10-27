import json
from pathlib import Path
import numpy as np
import pandas as pd
from joblib import load

from .config import EXCLUDED, RAW_TRAIN, SPLITS
from .metrics import binary_metrics

ROOT = Path(__file__).resolve().parents[1]

def main():
    data = pd.read_csv(RAW_TRAIN); split = pd.read_csv(SPLITS)
    valid = split["split"].eq("validation")
    X = data.drop(columns=EXCLUDED)
    model = load(ROOT / "evidencias/modelos/random_forest.joblib")
    score = model.predict_proba(X.loc[valid])[:, 1]; y = data.loc[valid, "label"]
    rows = []
    for threshold in np.arange(0, 1.001, 0.01):
        m = binary_metrics(y, score, round(float(threshold), 2))
        rows.append({"threshold":round(float(threshold),2), **{k:v for k,v in m.items() if k != "confusion_matrix"}, "confusion_matrix":m["confusion_matrix"]})
    table = pd.DataFrame(rows)
    feasible = table[table["fpr"] <= 0.05]
    chosen = feasible.sort_values(["recall_attack", "macro_f1", "precision_attack"], ascending=False).iloc[0].to_dict()
    table.to_csv(ROOT / "evidencias/umbral-sweep-random-forest.csv", index=False)
    (ROOT / "evidencias/seleccion-umbral.json").write_text(json.dumps({"model":"random_forest","criterion":"max recall_attack subject to fpr <= 0.05; ties macro_f1 then precision_attack","chosen":chosen,"validation_rows":int(valid.sum()),"test_used":False}, indent=2), encoding="utf-8")
    print(json.dumps(chosen, indent=2))

if __name__ == "__main__": main()
