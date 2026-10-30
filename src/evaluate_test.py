"""Evaluacion unica de test congelado y ensayo separado de validacion."""
import argparse, hashlib, json, subprocess
from pathlib import Path
import pandas as pd
import sklearn
from joblib import load
from huggingface_hub import snapshot_download
from .config import EXCLUDED, RAW_TEST, RAW_TRAIN, SPLITS
from .metrics import binary_metrics

ROOT = Path(__file__).resolve().parents[1]
TEST_SHA256 = "734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559"
MODEL_SHA256 = "5c18730460aadd105d0cd762165edb66ad2fcfec5afa89fbc1098eda83f74342"
HF_REPO = "Daniel-RGS/defiende-el-servidor-unsw-nb15"
HF_REVISION = "d71ac6a63d9a80ecc7af6c13601676a71b925da3"

def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def git_commit(): return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

def load_hf_model(output_dir):
    model_dir = snapshot_download(HF_REPO, revision=HF_REVISION, local_dir=output_dir / "hf-model", token=None)
    config = json.loads((Path(model_dir) / "config.json").read_text())
    threshold = float(config["threshold"])
    model_path = Path(model_dir) / "pipeline.joblib"
    verified_hash = sha256(model_path)
    if verified_hash != MODEL_SHA256: raise ValueError("SHA-256 del modelo no coincide; no se carga")
    return load(model_path), threshold, verified_hash

def validation_dry_run(output_dir):
    data = pd.read_csv(RAW_TRAIN); split = pd.read_csv(SPLITS); valid = split["split"].eq("validation")
    model, threshold, _ = load_hf_model(output_dir)
    X = data.drop(columns=EXCLUDED).loc[valid]
    metrics = binary_metrics(data.loc[valid, "label"], model.predict_proba(X)[:, 1], threshold)
    print(json.dumps({"mode":"validation_dry_run","rows":int(valid.sum()),"threshold":threshold,**metrics}, indent=2))

def evaluate_test(output_dir):
    pred_path, metrics_path = output_dir / "predicciones-test.csv", output_dir / "metricas-test.json"
    if pred_path.exists() or metrics_path.exists(): raise FileExistsError("Salidas ya existen; no se permite repetir la evaluacion")
    if sha256(RAW_TEST) != TEST_SHA256: raise ValueError("SHA-256 de test no coincide")
    model, threshold, model_hash = load_hf_model(output_dir)
    test = pd.read_csv(RAW_TEST)
    if len(test) != 82332: raise ValueError("El test no tiene 82.332 filas")
    X = test.drop(columns=EXCLUDED)
    assert len(X.columns) == 42, "El test no deja exactamente 42 predictoras"
    assert list(X.columns) == list(model.feature_names_in_), "El orden/nombre de predictoras no coincide con el modelo"
    score = model.predict_proba(X)[:, 1]; pred = (score >= threshold).astype(int)
    pd.DataFrame({"row_id":[f"testing-set:{i}" for i in range(len(test))],"y_true":test["label"],"score_attack":score,"y_pred":pred}).to_csv(pred_path,index=False)
    metrics = binary_metrics(test["label"], score, threshold)
    metrics_path.write_text(json.dumps({"version":"v2","model_sha256":model_hash,"dataset_sha256":TEST_SHA256,"rows":len(test),"threshold":threshold,"positive_class":1,"hf_revision":HF_REVISION,"git_commit":git_commit(),"scikit_learn":sklearn.__version__,**metrics},indent=2),encoding="utf-8")

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output-dir",type=Path,required=True); p.add_argument("--validation-dry-run",action="store_true"); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    validation_dry_run(a.output_dir) if a.validation_dry_run else evaluate_test(a.output_dir)
