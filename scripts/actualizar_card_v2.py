"""Sube a Hugging Face solo la model card de v2 con el resultado de test y verifica que el modelo no cambió.

Requiere sesión iniciada (`hf auth login`). Uso desde la raíz del repositorio:
    python scripts/actualizar_card_v2.py          # commit directo en main (dueño del repo)
    python scripts/actualizar_card_v2.py --pr     # Pull Request (cualquier cuenta)
"""
import argparse
from huggingface_hub import HfApi

REPO = "Daniel-RGS/defiende-el-servidor-unsw-nb15"
EVALUATED = "d71ac6a63d9a80ecc7af6c13601676a71b925da3"
MODEL_SHA256 = "5c18730460aadd105d0cd762165edb66ad2fcfec5afa89fbc1098eda83f74342"

def files(api, revision):
    return {f.path: (f.lfs.sha256 if f.lfs else f.blob_id) for f in api.list_repo_tree(REPO, revision=revision)}

p = argparse.ArgumentParser(); p.add_argument("--pr", action="store_true"); a = p.parse_args()
api = HfApi()
print("cuenta:", api.whoami()["name"])
info = api.upload_file(
    path_or_fileobj="model_cards/v2/README.md", path_in_repo="README.md", repo_id=REPO, revision="main", parent_commit=EVALUATED,  # falla si main ya no es la revisión evaluada
    commit_message="docs: agregar resultado de test a la model card de v2",
    commit_description=f"Solo documentación. Revisión evaluada {EVALUATED}; SHA-256 de pipeline.joblib {MODEL_SHA256}.",
    create_pr=a.pr)
new = info.oid
before, after = files(api, EVALUATED), files(api, new)
assert after["pipeline.joblib"] == before["pipeline.joblib"] == MODEL_SHA256, "pipeline.joblib cambió"
assert after["config.json"] == before["config.json"] and after["requirements.txt"] == before["requirements.txt"], "config o dependencias cambiaron"
print("nueva revisión (solo documentación):", new)
print("PR:", info.pr_url) if a.pr else None
print("pipeline.joblib sin cambios:", after["pipeline.joblib"])
