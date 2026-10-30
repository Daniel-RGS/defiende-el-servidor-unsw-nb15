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

## Respaldo DVC para recuperación sin credenciales

Respaldo externo: [archivo DVC en Drive](https://drive.google.com/file/d/1j7H_eR0oXREf799NVNKJ-N3yUl-Lag4b/view?usp=drive_link)

SHA-256 esperado del archivo descargado:

```text
9a8e05590a0d41110051662b956ca78455919968a86f2ee6cdd6a8fc193e620d
```

Después de descargarlo y extraerlo, el directorio `cache` extraído puede usarse
como remote local:

```bash
dvc remote add backup /ruta/al/cache-extraido
dvc pull -r backup
sha256sum data/raw/UNSW_NB15_training-set.csv data/raw/UNSW_NB15_testing-set.csv
```

La salida reproducida de esta prueba está en
`evidencias/recuperacion/dvc-pull-drive.log`.

## Pendientes para Miguel Nagel

La auditoría, los splits, el pipeline, los experimentos, la recuperación, la
evaluación única del test y sus evidencias ya están terminados y publicados.
Miguel debe cerrar estos puntos antes de la entrega:

- Actualizar la model card pública de Hugging Face de v2 con las métricas del
  test, manteniendo la revisión evaluada
  `d71ac6a63d9a80ecc7af6c13601676a71b925da3` y el mismo SHA de
  `pipeline.joblib`.
- Comprobar que la model card no incluya tokens, correos ni rutas personales.
- Preparar el informe final y completar `entrega.md` con la contribución de
  cada integrante y las limitaciones del resultado en test.
- Crear el ZIP final sin `.env`, cachés, entornos virtuales, `mlruns/` ni
  credenciales; verificar su contenido antes de enviarlo.
- Hacer una recuperación final desde una carpeta limpia y guardar la evidencia
  correspondiente.

Para continuar, Miguel necesita permisos de escritura en el repositorio de
GitHub. No se deben compartir tokens: cada persona configura sus credenciales
locales fuera de Git.
