import hashlib, json, platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "evidencias"
PREP = ROOT / "data" / "prepared"
SEED = 20261027
VALIDATION_SIZE = 0.20

EXPECTED = {
    "UNSW_NB15_training-set.csv": {"sha256": "bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa", "rows": 175341},
    "UNSW_NB15_testing-set.csv": {"sha256": "734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559", "rows": 82332},
}
SOURCE = "https://huggingface.co/datasets/Mouwiya/UNSW-NB15-small"
OFFICIAL = "https://research.unsw.edu.au/projects/unsw-nb15-dataset"
CATEGORICAL = ["proto", "service", "state"]
EXCLUDED = ["label", "attack_cat", "id"]

DESCRIPTIONS = {
    "id":"Identificador de la fila", "dur":"Duración total del flujo", "proto":"Protocolo de transacción",
    "service":"Servicio usado (por ejemplo http, ftp, smtp)", "state":"Estado de la conexión según el protocolo",
    "spkts":"Paquetes de origen a destino", "dpkts":"Paquetes de destino a origen",
    "sbytes":"Bytes de origen a destino", "dbytes":"Bytes de destino a origen", "rate":"Tasa del flujo",
    "sttl":"TTL de origen a destino", "dttl":"TTL de destino a origen", "sload":"Carga de origen en bits/s",
    "dload":"Carga de destino en bits/s", "sloss":"Paquetes de origen retransmitidos o perdidos",
    "dloss":"Paquetes de destino retransmitidos o perdidos", "sinpkt":"Intervalo entre paquetes de origen",
    "dinpkt":"Intervalo entre paquetes de destino", "sjit":"Jitter de origen", "djit":"Jitter de destino",
    "swin":"Ventana TCP de origen", "stcpb":"Número base TCP de origen", "dtcpb":"Número base TCP de destino",
    "dwin":"Ventana TCP de destino", "tcprtt":"Tiempo de ida y vuelta TCP", "synack":"Tiempo SYN a SYN-ACK",
    "ackdat":"Tiempo SYN-ACK a ACK", "smean":"Tamaño medio de paquetes de origen",
    "dmean":"Tamaño medio de paquetes de destino", "trans_depth":"Profundidad de transacción HTTP",
    "response_body_len":"Bytes del cuerpo de respuesta HTTP", "ct_srv_src":"Conexiones al servicio desde el origen",
    "ct_state_ttl":"Conexiones por estado y TTL", "ct_dst_ltm":"Conexiones al destino en la ventana temporal",
    "ct_src_dport_ltm":"Conexiones por origen y puerto destino", "ct_dst_sport_ltm":"Conexiones por destino y puerto origen",
    "ct_dst_src_ltm":"Conexiones entre destino y origen", "is_ftp_login":"Indica inicio de sesión FTP",
    "ct_ftp_cmd":"Conteo de comandos FTP", "ct_flw_http_mthd":"Conteo de métodos HTTP",
    "ct_src_ltm":"Conexiones desde el origen en la ventana temporal", "ct_srv_dst":"Conexiones al servicio y destino",
    "is_sm_ips_ports":"Indica mismas IP/puertos de origen y destino", "attack_cat":"Categoría del ataque (objetivo auxiliar; fuga de información)",
    "label":"Etiqueta binaria: 0 normal, 1 ataque",
}

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()

def counts(s): return {str(k): int(v) for k, v in s.value_counts(dropna=False).items()}

def main():
    OUT.mkdir(exist_ok=True); PREP.mkdir(exist_ok=True)
    downloaded = datetime.now(timezone.utc).isoformat()
    frames, files = {}, {}
    for name, expected in EXPECTED.items():
        path = RAW / name; digest = sha256(path); df = pd.read_csv(path)
        assert digest == expected["sha256"], (name, digest)
        assert len(df) == expected["rows"], (name, len(df))
        frames[name] = df
        files[name] = {"source": SOURCE, "official_reference": OFFICIAL, "downloaded_at_utc": downloaded,
                       "sha256": digest, "bytes": path.stat().st_size, "rows": len(df), "columns": len(df.columns),
                       "column_names": list(df.columns), "classes": counts(df["label"]),
                       "missing_by_column": {k:int(v) for k,v in df.isna().sum().items()},
                       "dtypes": {k:str(v) for k,v in df.dtypes.items()}}

    train = frames["UNSW_NB15_training-set.csv"].copy()
    predictors = [c for c in train.columns if c not in EXCLUDED]
    # String representation avoids numeric/string tuple ambiguity and is stable across runs.
    keys = train[predictors].fillna("<NA>").astype(str).agg("\\x1f".join, axis=1)
    group_sizes = keys.value_counts()
    contradictory = train.assign(_key=keys).groupby("_key")["label"].nunique()
    contradictory = contradictory[contradictory > 1]
    splitter = GroupShuffleSplit(n_splits=1, test_size=VALIDATION_SIZE, random_state=SEED)
    tr_idx, va_idx = next(splitter.split(train, train["label"], groups=keys))
    assignment = pd.DataFrame({"source_file":"UNSW_NB15_training-set.csv", "source_row_number":np.arange(len(train)),
                               "row_id": "train:" + pd.Series(np.arange(len(train)), dtype=str),
                               "split":"unassigned", "group_key_sha256":[hashlib.sha256(k.encode()).hexdigest() for k in keys]})
    assignment.loc[tr_idx, "split"] = "train"; assignment.loc[va_idx, "split"] = "validation"
    assignment.to_csv(PREP / "split_assignments.csv", index=False)
    # Save row references only; raw CSVs remain the DVC payload.
    pd.DataFrame({"row_id": assignment.loc[tr_idx,"row_id"]}).to_csv(PREP / "train_rows.csv", index=False)
    pd.DataFrame({"row_id": assignment.loc[va_idx,"row_id"]}).to_csv(PREP / "validation_rows.csv", index=False)
    split_hashes = {}
    for name, idx in [("train", tr_idx), ("validation", va_idx)]:
        split_hashes[name] = sha256(PREP / ("train_rows.csv" if name == "train" else "validation_rows.csv"))

    test = frames["UNSW_NB15_testing-set.csv"]
    test_keys = test[predictors].fillna("<NA>").astype(str).agg("\\x1f".join, axis=1)
    train_keys, val_keys = set(keys.iloc[tr_idx]), set(keys.iloc[va_idx])
    audit = {"generated_at_utc":downloaded, "seed":SEED, "validation_fraction":VALIDATION_SIZE,
             "files":files, "predictors":predictors, "categorical_predictors":CATEGORICAL,
             "excluded_columns":EXCLUDED, "variable_dictionary":
             [{"name":c,"dtype":str(train[c].dtype),"role":"categorical" if c in CATEGORICAL else ("excluded" if c in EXCLUDED else "numeric"),"meaning":DESCRIPTIONS.get(c,"")} for c in train.columns],
             "training_audit":{"predictor_duplicate_rows":int(len(train)-group_sizes.size),"unique_predictor_groups":int(group_sizes.size),
             "duplicate_groups":int((group_sizes>1).sum()),"max_group_size":int(group_sizes.max()),
             "contradictory_label_groups":int(len(contradictory)),"contradictory_rows":int(sum(group_sizes.loc[contradictory.index])),
             "contradiction_policy":"No predictor group is split. Contradictory-label groups are retained and assigned wholly to one split; they are flagged for analysis, never silently deduplicated or used to tune on test.",
             "train_rows":int(len(tr_idx)),"validation_rows":int(len(va_idx)),"train_class_counts":counts(train.iloc[tr_idx].label),"validation_class_counts":counts(train.iloc[va_idx].label),
             "split_group_overlap":int(len(set(keys.iloc[tr_idx]) & set(keys.iloc[va_idx]))),
             "split_assignment_sha256":sha256(PREP / "split_assignments.csv"),
             "row_reference_sha256":split_hashes,
             "validation_rationale":"20% permite una validación suficientemente grande y conserva 80% para entrenar; la asignación queda fija para comparar todos los experimentos."},
             "test_overlap_audit":{"test_predictor_groups":int(test_keys.nunique()),"test_rows_overlapping_train_groups":int(test_keys.isin(train_keys).sum()),"test_rows_overlapping_validation_groups":int(test_keys.isin(val_keys).sum()),"test_groups_overlapping_train":int(len(set(test_keys)&train_keys)),"test_groups_overlapping_validation":int(len(set(test_keys)&val_keys)),"note":"Audited using predictors only; test labels were not used for splitting, model or threshold selection."},
             "reproducibility":{"script":"audit_data.py","python":platform.python_version(),"assignment_file":"data/prepared/split_assignments.csv"}}
    (OUT/"auditoria.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT/"diccionario_variables.json").write_text(json.dumps(audit["variable_dictionary"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"files":files,"split":audit["training_audit"],"test_overlap":audit["test_overlap_audit"]}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
