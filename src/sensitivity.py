import json
from pathlib import Path
import pandas as pd
from joblib import load

from .config import EXCLUDED, RAW_TRAIN, SPLITS
from .metrics import binary_metrics

ROOT = Path(__file__).resolve().parents[1]

def main():
    data = pd.read_csv(RAW_TRAIN); assignment = pd.read_csv(SPLITS)
    predictors = [c for c in data.columns if c not in EXCLUDED]
    keys = data[predictors].fillna("<NA>").astype(str).agg("\x1f".join, axis=1)
    contradictory = data.assign(_key=keys).groupby("_key")["label"].nunique()
    contradictory_keys = set(contradictory[contradictory > 1].index)
    valid = assignment["split"].eq("validation")
    clean = valid & ~keys.isin(contradictory_keys)
    X = data.drop(columns=EXCLUDED)
    rows = []
    for path in sorted((ROOT / "evidencias/modelos").glob("*.joblib")):
        model = load(path)
        score = model.predict_proba(X.loc[valid])[:, 1]
        metrics = binary_metrics(data.loc[valid, "label"], score, 0.5)
        clean_score = model.predict_proba(X.loc[clean])[:, 1]
        clean_metrics = binary_metrics(data.loc[clean, "label"], clean_score, 0.5)
        rows.append({"model":path.stem,"validation_rows":int(valid.sum()),"sensitivity_rows":int(clean.sum()),"contradictory_rows_excluded":int(valid.sum()-clean.sum()),**{"all_"+k:v for k,v in metrics.items() if k != "confusion_matrix"},**{"without_contradictions_"+k:v for k,v in clean_metrics.items() if k != "confusion_matrix"}})
    (ROOT / "evidencias/metricas-sensibilidad.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(ROOT / "evidencias/metricas-sensibilidad.csv", index=False)
    print(json.dumps(rows, indent=2))

if __name__ == "__main__": main()
