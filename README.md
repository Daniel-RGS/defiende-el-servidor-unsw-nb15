# defiende-el-servidor-unsw-nb15

MLOps 2026-II: versionado de código, datos, experimentos y modelos con UNSW-NB15.
Clasificación binaria de conexiones: `0` normal y `1` ataque (clase positiva).

- Código: este repositorio (tags `v1`, `v2`, `freeze-pre-test`).
- Datos: DVC (`data/raw/*.dvc` y `data/prepared.dvc`).
- Experimentos: MLflow local, exportado en `evidencias/mlflow/<run_id>/`.
- Modelos: Hugging Face Hub, [`Daniel-RGS/defiende-el-servidor-unsw-nb15`](https://huggingface.co/Daniel-RGS/defiende-el-servidor-unsw-nb15).

El índice de evidencias y las referencias de cada versión están en `entrega.md`.

## Requisitos

- Python 3.12 (probado con 3.12.3 en el equipo de entrenamiento y 3.12.14 en la recuperación).
- Git. Las dependencias están fijadas en `requirements.txt`.

## 1. Instalación

```bash
git clone https://github.com/Daniel-RGS/defiende-el-servidor-unsw-nb15.git
cd defiende-el-servidor-unsw-nb15
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

En un Mac Intel (x86_64), `cryptography==50.0.2` no tiene rueda precompilada.
Ahí basta con instalar `cryptography==48.0.1` en su lugar; ese paquete no
interviene en los datos ni en los modelos:

```bash
sed 's/^cryptography==50.0.2$/cryptography==48.0.1/' requirements.txt > requirements-mac-intel.txt
pip install -r requirements-mac-intel.txt
```

## 2. Recuperación de datos con DVC

Los CSV no están en Git. La vía que no requiere credenciales es el respaldo del
almacenamiento DVC publicado en Drive
([enlace](https://drive.google.com/file/d/1j7H_eR0oXREf799NVNKJ-N3yUl-Lag4b/view?usp=drive_link)),
SHA-256 `9a8e05590a0d41110051662b956ca78455919968a86f2ee6cdd6a8fc193e620d`.
Contiene la carpeta `cache/`, que se usa como remote DVC:

```bash
pip install gdown==5.2.0
gdown 1j7H_eR0oXREf799NVNKJ-N3yUl-Lag4b --output ../dvc-storage.tar.gz
shasum -a 256 ../dvc-storage.tar.gz        # en Linux: sha256sum
tar -xzf ../dvc-storage.tar.gz -C ..
dvc remote add --local backup "$(cd .. && pwd)/cache"
dvc pull -r backup
shasum -a 256 data/raw/*.csv data/prepared/split_assignments.csv
```

Huellas esperadas:

```text
bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa  data/raw/UNSW_NB15_training-set.csv
734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559  data/raw/UNSW_NB15_testing-set.csv
8a6538f6423a503e76cdf82ebbbf73c1449689d27388de4e1e34a3abf8eded8c  data/prepared/split_assignments.csv
```

El remote por defecto (`origin`, DagsHub) requiere credenciales del propietario.
Quien tenga acceso las configura solo en `.dvc/config.local`, que no se publica:

```bash
dvc remote modify origin --local access_key_id "$DAGSHUB_TOKEN"
dvc remote modify origin --local secret_access_key "$DAGSHUB_TOKEN"
dvc pull -r origin
```

## 3. Ejecutar un experimento

Cada corrida entrena con `train` y evalúa con `validation` de los splits fijos,
y queda registrada en MLflow local (`mlruns/`). Para reproducir una sola sin
tocar `evidencias/`:

```bash
python -m src.run_experiments --only random_forest --output-dir reproduccion/random_forest
mlflow ui   # opcional, para consultar las corridas en http://127.0.0.1:5000
```

Identificadores disponibles: `logistic_baseline`, `logistic_balanced`,
`logistic_regularization`, `tree_baseline`, `tree_balanced`, `random_forest`.
En nuestro equipo tardaron unos 63 s (logística) y 119 s (bosque), con menos de
800 MB de memoria; el detalle está en `evidencias/reproduccion-experimento.json`.

## 4. Descargar cada modelo y predecir

Los modelos se descargan por SHA completo de Hugging Face y solo se cargan si el
SHA-256 de `pipeline.joblib` coincide con el registrado:

| Versión | Revisión Hugging Face | SHA-256 de `pipeline.joblib` | Umbral |
|---|---|---|---|
| v1 | `c4ed6901110c506b99438df76933c779fc9e737c` | `3cf85c943fc34d5d978c84da5f08ca4bc252d61ba72f73fdafabd6792deefbff` | 0.50 |
| v2 | `d71ac6a63d9a80ecc7af6c13601676a71b925da3` | `5c18730460aadd105d0cd762165edb66ad2fcfec5afa89fbc1098eda83f74342` | 0.51 |

La model card pública de v2 fue actualizada con las métricas del test en la
revisión `167253b06ef31532460256e74b52a44c87af3405`; la revisión evaluada sigue
siendo `d71ac6a63d9a80ecc7af6c13601676a71b925da3` y el SHA de `pipeline.joblib`
no cambió.

```bash
python -m src.predict --version v1 --input evidencias/recuperacion/entrada-validacion-20.csv --output pred-v1.csv
python -m src.predict --version v2 --input evidencias/recuperacion/entrada-validacion-20.csv --output pred-v2.csv
```

La entrada es un CSV con las 42 predictoras; `id`, `label`, `attack_cat` y
`row_id` se ignoran si aparecen. La salida tiene `row_id`, `score_attack` y
`y_pred`, con la regla `y_pred = 1` si `score_attack >= umbral`.

## 5. Prueba de recuperación completa

Compara las predicciones de v1 y v2 recuperadas con las guardadas antes de
publicar (tolerancia `1e-12`):

```bash
python -m src.recover
```

Para repetirla desde cero en una carpeta y un entorno nuevos (clona, instala,
baja el respaldo DVC de Drive, verifica huellas, descarga v1/v2 por SHA y
compara):

```bash
bash scripts/recuperacion_limpia.sh <commit-o-tag> 2>&1 | tee recuperacion.log
```

La ejecución entregada está en `evidencias/recuperacion/final/`.

## 6. Evaluación de test

La evaluación única ya se hizo y no debe repetirse: `src/evaluate_test.py`
se niega a sobrescribir sus salidas. Las métricas se recalculan desde las
predicciones por fila:

```bash
python -m src.recalculate_test_metrics evidencias/test-final/predicciones-test.csv
```
