# defiende-el-servidor-unsw-nb15
MLOps 2026-II: versionado de código, datos, experimentos y modelos con UNSW-NB15

## Recuperación de datos con DVC

Los CSV no se almacenan en Git. Se recuperan desde el remote DVC de DagsHub. Las
credenciales se configuran únicamente en `.dvc/config.local` y nunca se publican.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configurar localmente las credenciales; no copiar .dvc/config.local desde otro equipo.
dvc remote modify origin --local access_key_id "$DAGSHUB_TOKEN"
dvc remote modify origin --local secret_access_key "$DAGSHUB_TOKEN"
dvc pull -r origin

sha256sum data/raw/UNSW_NB15_training-set.csv
sha256sum data/raw/UNSW_NB15_testing-set.csv
```

Hashes esperados:

```text
bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa  data/raw/UNSW_NB15_training-set.csv
734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559  data/raw/UNSW_NB15_testing-set.csv
```

Para versionar una nueva copia recibida:

```bash
dvc add data/raw/UNSW_NB15_training-set.csv data/raw/UNSW_NB15_testing-set.csv
git add .dvc .dvcignore .gitignore data/raw/*.dvc data/raw/.gitignore
git commit -m "data: versionar datasets UNSW-NB15 con DVC"
git push origin HEAD
dvc push -r origin
```
