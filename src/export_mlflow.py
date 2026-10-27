import hashlib, json, shutil
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidencias"
HYPOTHESES = {
    "logistic_baseline": ("Si uso una regresion logistica regularizada como referencia, espero un modelo interpretable con buen recall porque separa linealmente tras el preprocesamiento.", "Referencia establecida; sirve como v1."),
    "logistic_balanced": ("Si cambio solo class_weight a balanced, espero cambiar el equilibrio recall/FPR porque penalizo mas los errores de la clase ataque.", "No aumento recall frente a la referencia y redujo FPR; la hipotesis no se cumplio literalmente."),
    "logistic_regularization": ("Si cambio solo C a 0.1, espero reducir sobreajuste y mejorar macro-F1 porque impongo mas regularizacion.", "Macro-F1 bajo frente a la referencia; la hipotesis no se cumplio."),
    "tree_baseline": ("Si cambio la familia a un arbol de profundidad 12, espero capturar relaciones no lineales porque divide el espacio por reglas.", "Supero a las logisticas en macro-F1; la hipotesis se cumplio parcialmente."),
    "tree_balanced": ("Si cambio solo class_weight a balanced en el arbol, espero reducir FPR y aceptar menor recall porque pondero mas los errores de ataque.", "FPR bajo mucho y recall tambien; la hipotesis se cumplio en el intercambio esperado."),
    "random_forest": ("Si cambio el arbol por un conjunto balanceado de 100 arboles, espero reducir sobreajuste porque promedia arboles distintos, manteniendo class_weight=balanced.", "Mejoro macro-F1 y FPR frente al arbol balanceado; la hipotesis se cumplio para esas metricas."),
}

def sha256(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def main():
    table = pd.read_csv(EVID / "experimentos.csv")
    table["hypothesis"] = table["id"].map(lambda x: HYPOTHESES[x][0])
    table["conclusion"] = table["id"].map(lambda x: HYPOTHESES[x][1])
    table.to_csv(EVID / "experimentos.csv", index=False)
    out = EVID / "mlflow"; out.mkdir(exist_ok=True)
    for _, row in table.iterrows():
        run = out / row.run_id; run.mkdir(exist_ok=True)
        params = {"family":row.family,"seed":int(row.seed),"git_commit":row.git_commit,"dvc_version":row.dvc_version,"hypothesis":row.hypothesis,"threshold":float(row.threshold)}
        (run/"params.json").write_text(json.dumps(params, indent=2), encoding="utf-8")
        metrics = {k:float(row[k]) for k in ["recall_attack","precision_attack","fpr","macro_f1","threshold"]}
        metrics["confusion_matrix"] = json.loads(row.confusion_matrix)
        (run/"metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        model = EVID / "modelos" / f"{row.id}.joblib"
        if model.exists():
            shutil.copy2(model, run / "model.joblib")
            (run/"artifact.json").write_text(json.dumps({"path":"model.joblib","sha256":sha256(model)}, indent=2), encoding="utf-8")
        (run/"metadata.json").write_text(json.dumps({"run_id":row.run_id,"experiment_name":"defiende-servidor-unsw-nb15","validation_only":True}, indent=2), encoding="utf-8")

if __name__ == "__main__": main()
