"""Evaluación única de test congelado. No ejecutar hasta autorizar la evaluación final."""
import argparse, hashlib, json
from pathlib import Path
import pandas as pd
from joblib import load
from huggingface_hub import snapshot_download
from .config import RAW_TEST
from .metrics import binary_metrics

ROOT = Path(__file__).resolve().parents[1]
TEST_SHA256 = "734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559"
MODEL_SHA256 = "5c18730460aadd105d0cd762165edb66ad2fcfec5afa89fbc1098eda83f74342"
HF_REPO = "Daniel-RGS/defiende-el-servidor-unsw-nb15"
HF_REVISION = "d71ac6a63d9a80ecc7af6c13601676a71b925da3"
THRESHOLD = 0.51

def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main(output_dir):
    if sha256(RAW_TEST) != TEST_SHA256: raise ValueError("SHA-256 de test no coincide")
    model_dir = snapshot_download(HF_REPO, revision=HF_REVISION, local_dir=output_dir / "hf-model", token=None)
    model_path = Path(model_dir) / "pipeline.joblib"
    if sha256(model_path) != MODEL_SHA256: raise ValueError("SHA-256 del modelo no coincide")
    test = pd.read_csv(RAW_TEST); X = test.drop(columns=["label", "attack_cat", "id"])
    score = load(model_path).predict_proba(X)[:, 1]
    pred = (score >= THRESHOLD).astype(int)
    out = output_dir / "predicciones-test.csv"
    pd.DataFrame({"row_id":[f"test:{i}" for i in range(len(test))],"y_true":test["label"],"score_attack":score,"y_pred":pred}).to_csv(out,index=False)
    metrics = binary_metrics(test["label"], score, THRESHOLD)
    (output_dir / "metricas-test.json").write_text(json.dumps({"version":"v2","model_sha256":MODEL_SHA256,"dataset_sha256":TEST_SHA256,"rows":len(test),"threshold":THRESHOLD,"positive_class":1,"hf_revision":HF_REVISION,**metrics},indent=2),encoding="utf-8")

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output-dir",type=Path,required=True); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); main(a.output_dir)
