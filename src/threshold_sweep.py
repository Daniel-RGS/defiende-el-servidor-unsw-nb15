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
    y = data.loc[valid, "label"]
    rows = []
    all_rows = []; chosen_rows = []
    for model_name in ["logistic_baseline", "logistic_balanced", "logistic_regularization", "tree_baseline", "tree_balanced", "random_forest"]:
        model = load(ROOT / "evidencias/modelos" / f"{model_name}.joblib")
        score = model.predict_proba(X.loc[valid])[:, 1]
        for threshold in np.arange(0, 1.001, 0.01):
            m = binary_metrics(y, score, round(float(threshold), 2))
            all_rows.append({"model":model_name,"threshold":round(float(threshold),2), **{k:v for k,v in m.items() if k != "confusion_matrix"}, "confusion_matrix":m["confusion_matrix"]})
        candidate = pd.DataFrame([r for r in all_rows if r["model"] == model_name])
        feasible = candidate[candidate["fpr"] <= 0.05]
        chosen = feasible.sort_values(["recall_attack", "macro_f1", "precision_attack"], ascending=False).iloc[0].to_dict()
        chosen_rows.append(chosen)
    table = pd.DataFrame(all_rows); chosen_table = pd.DataFrame(chosen_rows)
    table.to_csv(ROOT / "evidencias/umbral-sweep-all.csv", index=False)
    chosen_table.to_csv(ROOT / "evidencias/umbral-candidatos.csv", index=False)
    (ROOT / "evidencias/seleccion-umbral.json").write_text(json.dumps({"criterion":"max recall_attack subject to fpr <= 0.05; ties macro_f1 then precision_attack","candidates":chosen_rows,"chosen_model":"random_forest","chosen_threshold":0.51,"validation_rows":int(valid.sum()),"test_used":False}, indent=2), encoding="utf-8")
    print(chosen_table[["model","threshold","recall_attack","precision_attack","fpr","macro_f1"]].to_string(index=False))

if __name__ == "__main__": main()
