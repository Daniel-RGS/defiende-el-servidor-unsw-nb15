# Entrega: MLOps, Defiende el servidor

## Integrantes y repositorio

- Miguel Melo, grupo A.
- Daniel Santiago Rincón Gamba, grupo B.
- GitHub: https://github.com/Daniel-RGS/defiende-el-servidor-unsw-nb15
- Commit final de la entrega: el que señala el tag `entrega-final`. Su SHA
  completo va en el mensaje de entrega y en `COMMIT_ENTREGA.txt` dentro del ZIP
  (un archivo no puede contener el SHA del commit que lo incluye).
- Hugging Face: https://huggingface.co/Daniel-RGS/defiende-el-servidor-unsw-nb15

## Versiones

| Campo | v1 | v2 |
|---|---|---|
| Modelo | regresión logística (`logistic_baseline`) | random forest balanceado, 100 árboles, `max_depth=18` |
| Commit que entrenó el modelo | `7c35ad5b8734ab5fb8f5b100d7284ba01838a01c` | `7c35ad5b8734ab5fb8f5b100d7284ba01838a01c` |
| Tag y revisión de código | `v1` = `dc23c56e58f71e86eb4e07451ba6d7d03f1880dc` | `v2` = `b453a7fe4017435b81b517b3458c57fc172d3374` |
| Configuración | `configs/v1.json` | `configs/v2.json` |
| Datos DVC | `data/prepared.dvc` (`md5 3d25c4d99b4554f739dccd6e0a2dbe07.dir`), commit `be164fb7bc1aad823b2bfeeb3c97f3e98ba043e4` | igual que v1 |
| Run de MLflow | `69f2df8e614b4efc8cea9ea98e442368` | `dcdbd1d174e442039826cfb6d38ccb99` |
| Revisión Hugging Face | `c4ed6901110c506b99438df76933c779fc9e737c` | `d71ac6a63d9a80ecc7af6c13601676a71b925da3` |
| SHA-256 de `pipeline.joblib` | `3cf85c943fc34d5d978c84da5f08ca4bc252d61ba72f73fdafabd6792deefbff` | `5c18730460aadd105d0cd762165edb66ad2fcfec5afa89fbc1098eda83f74342` |
| Umbral | 0.50 | 0.51 |
| Validación (recall, precision, FPR, macro-F1) | 0.9881, 0.9246, 0.1712, 0.9247 | 0.9463, 0.9762, 0.0490, 0.9410 |

Las dos versiones salieron del mismo commit de entrenamiento porque las seis
corridas se registraron juntas. Para que las revisiones de código sean
distinguibles, los tags `v1` y `v2` apuntan a commits posteriores distintos que
fijan `configs/v1.json` y `configs/v2.json`.

v2 cambia la familia de modelo (logística a bosque balanceado) y el umbral
(0.50 a 0.51). Gana precision y baja el FPR de 0.171 a 0.049 en validación;
pierde recall (0.988 a 0.946). Aceptamos más ataques no detectados a cambio de
reducir las falsas alarmas a la cuarta parte.

La revisión `d71ac6a6...` es la que evaluamos en test y la que se descarga para
predecir. La model card de v2 con el resultado del test está en
`model_cards/v2/README.md`. Se publica en Hugging Face con
`scripts/actualizar_card_v2.py`, que hace un commit de solo documentación sobre
`d71ac6a6...` y comprueba que `pipeline.joblib`, `config.json` y
`requirements.txt` no cambian. El SHA de la revisión de Hugging Face con la card
actualizada se indica en el mensaje de entrega.

## Datos

- Originales: `data/raw/UNSW_NB15_training-set.csv.dvc` (md5
  `e55caabaa6cd4a8f1c06a227bcfababc`) y `data/raw/UNSW_NB15_testing-set.csv.dvc`
  (md5 `e0beea40262e46168cdb81476dbc27b4`), commit
  `5b646e2d4dd919de0bc67a38260e224831871404`.
- Preparados y splits: `data/prepared.dvc`, commit
  `be164fb7bc1aad823b2bfeeb3c97f3e98ba043e4`. Contiene `train.csv` (139.850
  filas), `validation.csv` (35.491), `split_assignments.csv`, `train_rows.csv` y
  `validation_rows.csv`.
- SHA-256 de los CSV recibidos: entrenamiento
  `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`, test
  `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`. Coinciden
  con las huellas del anexo de la guía.

### Almacenamiento DVC y acceso

- Vía para revisión sin credenciales: respaldo del almacenamiento DVC en Drive,
  https://drive.google.com/file/d/1j7H_eR0oXREf799NVNKJ-N3yUl-Lag4b/view?usp=drive_link
  (cualquiera con el enlace puede descargarlo). SHA-256
  `9a8e05590a0d41110051662b956ca78455919968a86f2ee6cdd6a8fc193e620d`. Se extrae
  y la carpeta `cache/` se usa como remote: pasos en el README, sección 2.
- Remote por defecto `origin`: DagsHub (`.dvc/config`), con credenciales del
  propietario. El acceso anónimo falla, como documentan
  `evidencias/recuperacion/dvc-pull-sin-credenciales.log` y
  `dvc-pull-public-https-sin-credenciales.log`. Por eso entregamos el respaldo.
- No hay tokens en Git ni en el ZIP; cada persona configura los suyos en
  `.dvc/config.local`.

## Ubicación de las evidencias

| Evidencia | Archivo |
|---|---|
| Auditoría (fuentes, SHA-256, filas, clases, faltantes, duplicados, contradicciones, splits, cruces) | `evidencias/auditoria.json`, `evidencias/diccionario_variables.json`, `audit_data.py` |
| Tabla de experimentos | `evidencias/experimentos.csv` (seis corridas) y `evidencias/<id>.json` |
| Análisis sin grupos contradictorios | `evidencias/metricas-sensibilidad.csv` y `.json` |
| Criterio y barrido de umbrales | `evidencias/criterio-seleccion.json`, `umbral-sweep-all.csv`, `umbral-candidatos.csv`, `seleccion-umbral.json` |
| Selección congelada | `evidencias/seleccion.json`, tag `freeze-pre-test` |
| Test final | `evidencias/test-final/metricas-test.json`, `evidencias/test-final/predicciones-test.csv`, `evidencias/evaluacion-test.log` |
| Exportación de MLflow | `evidencias/mlflow/<run_id>/` (params, metrics, metadata, artifact) |
| Recuperación final en entorno nuevo | `evidencias/recuperacion/final/` |
| Recuperaciones anteriores | `evidencias/recuperacion/*.log` |
| Reproducción de un experimento | `evidencias/reproduccion-experimento.json` |
| Model cards | `model_cards/v1/`, `model_cards/v2/` |
| Informe | `informe.pdf` (se entrega aparte del ZIP) |

## Comandos

Todos están en el README y se ejecutan desde la raíz del repositorio:

- Instalación: README, sección 1.
- Recuperación de datos: README, sección 2.
- Entrenamiento de un experimento:
  `python -m src.run_experiments --only random_forest --output-dir reproduccion/random_forest`.
- Predicción: `python -m src.predict --version v2 --input evidencias/recuperacion/entrada-validacion-20.csv --output pred-v2.csv`.
- Recuperación completa en carpeta nueva:
  `bash scripts/recuperacion_limpia.sh <commit> 2>&1 | tee recuperacion.log`.
- Recalcular métricas de test:
  `python -m src.recalculate_test_metrics evidencias/test-final/predicciones-test.csv`.
- Armar el ZIP desde Git (sin datos, entornos, cachés ni credenciales):
  `bash scripts/empaquetar_entrega.sh entrega-final <carpeta-salida>`.

### Tiempo y recursos medidos

Equipo de la recuperación final: Mac Intel Core i3-1000NG4 (2 núcleos, 1,1 GHz),
8 GB de RAM, macOS, Python 3.12.14.

- Recuperación completa desde cero (instalar, bajar datos y modelos, comparar):
  175 s (log en `evidencias/recuperacion/final/`; pip reutilizó su caché de paquetes, no de datos ni modelos).
- Entrenar `logistic_baseline`: 63 s y 729 MB de memoria máxima.
- Entrenar `random_forest`: 119 s y 759 MB de memoria máxima.

## Decisiones y notas de trazabilidad

**Splits.** Semilla `20261027`, validación del 20 % con `GroupShuffleSplit`.
El grupo es la representación de las 42 predictoras (todas las columnas menos
`id`, `label` y `attack_cat`), así que ningún grupo de entradas idénticas queda
repartido: el número de grupos compartidos entre train y validación es cero.
Hay 9.748 grupos repetidos (74.301 filas más allá de la primera aparición) y
229 grupos con etiquetas contradictorias (940 filas). Los conservamos completos
en una sola partición y los marcamos para análisis; no los eliminamos ni los
relabelamos por mayoría para no alterar la distribución.

**Solapamiento con test.** Auditado solo con predictoras: 6.886 filas de test
(8,36 %) repiten grupos de train y 1.655 (2,01 %) grupos de validación, cerca de
10,4 % en total. Esto puede favorecer las métricas de test.

**Criterio de selección.** Lo fijamos el 27 de octubre de 2026, antes del
barrido de umbrales: maximizar recall de ataque con FPR de validación como
máximo 5 %; en empates, macro-F1 y luego precision. Lo redactamos después de ver
las métricas con umbral 0.5 de las seis corridas, y así lo declaramos. El barrido
aplicó la misma rejilla (0.00 a 1.00 cada 0.01) a los seis candidatos. Ganó
random forest con 0.51 (recall 0.9463, FPR 0.0490); el siguiente fue el árbol
balanceado (recall 0.9291, FPR 0.0458). El margen frente al 5 % era pequeño.

**Congelación.** El tag `freeze-pre-test` apunta a
`eaaa2e622a24b142971c2060bcfe94f8121be2fc` (2026-10-27 17:51:40, hora de
Bogotá), publicado antes de leer el test. Agregamos el tag después, como marcador
del mismo commit. Los cambios posteriores de `seleccion.json` solo agregaron
referencias de commits y tags.

**Test.** `src/evaluate_test.py` cargó v2 por SHA, verificó los hashes del
modelo y del test, comprobó las 42 predictoras y aplicó `y_pred = 1` si
`score_attack >= 0.51`. Lo ejecutamos una sola vez, el 30 de octubre de 2026, sobre
las 82.332 filas, y el script se niega a sobrescribir sus salidas. Matriz
`[[30983, 6017], [1591, 43741]]`; recall 0.9649, precision 0.8791, FPR 0.1626,
macro-F1 0.9053. El ensayo previo sobre validación
(`evidencias/recuperacion/validation-dry-run.log`) reprodujo la matriz de
validación exacta.

**Hipótesis.** Las hipótesis breves quedaron en MLflow al ejecutar cada corrida.
La redacción ampliada ("si cambio X, espero Y, porque Z") y las conclusiones de
`experimentos.csv` las agregamos después, y lo declaramos así.

**MLflow.** Regeneramos el export con `src/export_mlflow.py` leyendo cada run
con `mlflow.get_run(run_id)`; no lo editamos a mano.

**Denominadores cero.** Precision, recall y macro-F1 usan `zero_division=0`, y
el FPR vale 0 si no hay negativos reales (`src/metrics.py`). En nuestros datos
no ocurrió.

**Diferencias de entorno.** En Mac Intel, `cryptography==50.0.2` no tiene rueda
y usamos 48.0.1 (no interviene en datos ni modelos). Reentrenar
`logistic_baseline` en ese equipo cambió 4 de 35.491 predicciones de validación
por diferencias numéricas del optimizador; `random_forest` se reprodujo exacto.
El artefacto entregado no se reentrena: se descarga por SHA.

## Limitaciones

- El FPR en test (0.163) triplica el de validación (0.049) y supera el límite
  de 5 % que guió la selección. Las particiones publicadas tienen distinta
  composición (44,9 % normal en test frente a 31,9 % en entrenamiento) y el
  tráfico normal del test genera más falsas alarmas. No reajustamos el umbral.
- Cerca del 10,4 % del test repite grupos vistos en train o validación.
- Las métricas pesan cada fila, incluidas repeticiones; 940 filas de validación
  tienen etiquetas contradictorias y ponen un techo a cualquier modelo.
- El criterio de umbral se escribió después de ver las métricas a 0.5 de
  validación (no las de test).
- UNSW-NB15 es un conjunto histórico de laboratorio; no demuestra eficacia en
  una red actual.
- El remote DagsHub requiere credenciales; la recuperación del docente depende
  del respaldo en Drive.

## Uso de IA, código externo y contribuciones

- Daniel usó Codex (OpenAI) para organizar el repositorio, escribir los scripts
  de auditoría, configurar DVC y revisar comandos. Verificó los SHA-256, filas,
  columnas, tipos, faltantes, duplicados, contradicciones, la asignación por
  grupos, la ausencia de secretos y las recuperaciones desde carpetas limpias.
- Miguel usó Claude Code (Anthropic) para escribir `src/predict.py`,
  `src/recover.py` y `scripts/recuperacion_limpia.sh`, actualizar el README,
  esta entrega, la model card de v2 y el informe, y ejecutar la recuperación
  final. Verificó que las predicciones recuperadas coincidieran, que una
  referencia alterada hiciera fallar la comparación, que las métricas de test se
  recalcularan iguales y que no hubiera secretos en Git ni en el ZIP.
- No copiamos código externo; usamos las bibliotecas listadas en
  `requirements.txt` con sus licencias. Datos: UNSW-NB15 (Moustafa y Slay, UNSW
  Canberra), obtenidos de una copia cuyas huellas coinciden con el anexo.
- Daniel Santiago Rincón Gamba: auditoría, DVC y respaldo, splits, seis
  experimentos en MLflow, selección de umbral, publicación de v1 y v2 en Hugging
  Face y evaluación única de test.
- Miguel Melo: recuperación final en entorno nuevo y sus scripts, reproducción
  de un experimento, actualización de la model card de v2 con el test, README,
  `entrega.md`, informe y paquete de entrega.
- La interpretación de las métricas y la defensa de las decisiones son de los
  dos integrantes.
