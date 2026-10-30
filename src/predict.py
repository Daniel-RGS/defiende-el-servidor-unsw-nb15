"""Descarga v1 o v2 desde Hugging Face por SHA completo, verifica el hash y predice."""
import argparse, hashlib, json
from pathlib import Path
import pandas as pd
from joblib import load
from huggingface_hub import snapshot_download
from .config import EXCLUDED

HF_REPO = "Daniel-RGS/defiende-el-servidor-unsw-nb15"
VERSIONS = {
    "v1": {"revision": "c4ed6901110c506b99438df76933c779fc9e737c", "model_sha256": "3cf85c943fc34d5d978c84da5f08ca4bc252d61ba72f73fdafabd6792deefbff"},
    "v2": {"revision": "d71ac6a63d9a80ecc7af6c13601676a71b925da3", "model_sha256": "5c18730460aadd105d0cd762165edb66ad2fcfec5afa89fbc1098eda83f74342"},
}

def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_version(version, download_dir):
    """Devuelve modelo, umbral e información de la revisión; no carga si el hash no coincide."""
    spec = VERSIONS[version]
    model_dir = Path(snapshot_download(HF_REPO, revision=spec["revision"], local_dir=Path(download_dir) / version, token=None))
    config = json.loads((model_dir / "config.json").read_text())
    model_path = model_dir / "pipeline.joblib"
    model_hash = sha256(model_path)
    if model_hash != spec["model_sha256"]: raise ValueError(f"SHA-256 de {version} no coincide: {model_hash}")
    info = {"version": version, "hf_repo": HF_REPO, "hf_revision": spec["revision"], "model_sha256": model_hash, "threshold": float(config["threshold"])}
    return load(model_path), info

def predict_frame(model, threshold, frame):
    """Regla del umbral: y_pred = 1 (ataque) si score_attack >= umbral."""
    X = frame.drop(columns=[c for c in EXCLUDED + ["row_id"] if c in frame.columns])
    if list(X.columns) != list(model.feature_names_in_): raise ValueError("Las predictoras no coinciden con las del modelo")
    score = model.predict_proba(X)[:, 1]
    return pd.DataFrame({"row_id": frame["row_id"] if "row_id" in frame else range(len(frame)), "score_attack": score, "y_pred": (score >= threshold).astype(int)})

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--version", choices=sorted(VERSIONS), required=True)
    p.add_argument("--input", type=Path, required=True, help="CSV con las 42 predictoras (id, label, attack_cat y row_id se ignoran)")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--download-dir", type=Path, default=Path("modelos-hf"))
    a = p.parse_args()
    model, info = load_version(a.version, a.download_dir)
    predict_frame(model, info["threshold"], pd.read_csv(a.input)).to_csv(a.output, index=False)
    print(json.dumps(info, indent=2))
