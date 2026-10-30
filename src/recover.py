"""Prueba de recuperación: predice con v1 y v2 descargadas por SHA y compara con las salidas guardadas."""
import argparse, json
from pathlib import Path
import pandas as pd
from .config import RAW_TRAIN, SPLITS
from .predict import load_version, predict_frame, sha256

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidencias/recuperacion"
INPUT = EVID / "entrada-validacion-20.csv"
TOLERANCE = 1e-12

def build_input():
    """Materializa las 20 filas fijas de validación usadas como referencia antes de publicar en HF."""
    row_ids = pd.read_csv(EVID / "v1-predictions-before-hf.csv")["row_id"]
    index = [int(r.split(":")[1]) for r in row_ids]
    split = pd.read_csv(SPLITS)
    if not split.loc[index, "split"].eq("validation").all(): raise ValueError("Alguna fila de referencia no es de validación")
    rows = pd.read_csv(RAW_TRAIN).loc[index]
    rows.insert(0, "row_id", list(row_ids))
    rows.to_csv(INPUT, index=False)
    print(f"{INPUT.relative_to(ROOT)}: {len(rows)} filas de validación, sha256 {sha256(INPUT)}")

def compare(version, download_dir, output_dir):
    model, info = load_version(version, download_dir)
    after = predict_frame(model, info["threshold"], pd.read_csv(INPUT))
    after.to_csv(output_dir / f"{version}-predictions-after-recovery.csv", index=False)
    before = pd.read_csv(EVID / f"{version}-predictions-before-hf.csv")
    if list(before["row_id"]) != list(after["row_id"]): raise ValueError("Las filas no coinciden con la referencia")
    diff = float((before["score_attack"] - after["score_attack"]).abs().max())
    result = {**info, "rows": len(after), "input_sha256": sha256(INPUT), "tolerance": TOLERANCE,
              "max_score_difference": diff, "labels_equal": bool(before["y_pred"].eq(after["y_pred"]).all())}
    result["ok"] = result["labels_equal"] and diff <= TOLERANCE
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--build-input", action="store_true")
    p.add_argument("--output-dir", type=Path, default=Path("recuperacion-salidas"))
    p.add_argument("--download-dir", type=Path, default=Path("modelos-hf"))
    a = p.parse_args()
    if a.build_input: build_input(); raise SystemExit
    a.output_dir.mkdir(parents=True, exist_ok=True)
    results = [compare(v, a.download_dir, a.output_dir) for v in ("v1", "v2")]
    (a.output_dir / "comparacion.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    if not all(r["ok"] for r in results): raise SystemExit("La recuperación no reproduce las salidas guardadas")
