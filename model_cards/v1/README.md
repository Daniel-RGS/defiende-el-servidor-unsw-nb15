---
library_name: scikit-learn
tags:
- network-intrusion-detection
- unsw-nb15
---

# Defiende el servidor — v1

## Propósito

Clasificación binaria de flujos UNSW-NB15: `0` normal y `1` ataque.

## Modelo y datos

Regresión logística regularizada dentro de un único pipeline scikit-learn. El
preprocesamiento imputa, codifica `proto`, `service`, `state` con one-hot y
escala las variables numéricas. Las columnas `id`, `attack_cat` y `label` no
entran al modelo. El umbral es `0.50`.

Se usaron los splits fijos de `data/prepared.dvc`, semilla `20261027`, y solo
validación para seleccionar/reportar el modelo. Test no se usó.

El artefacto se distribuye en formato `joblib`; cárguelo únicamente desde esta
revisión verificada y no desde archivos joblib de procedencia desconocida.

## Validación

Recall ataque: 0.9881; precision ataque: 0.9246; FPR: 0.1712; macro-F1:
0.9247. Matriz de confusión: `[[9414, 1944], [288, 23845]]`.

## Limitaciones y uso

La validación pesa cada fila, incluidas repeticiones. El dataset es histórico y
no demuestra eficacia sobre redes actuales. El umbral debe revisarse con datos
de operación; no usar `attack_cat` como entrada.

## Trazabilidad

- Git commit del código: `7c35ad5b8734ab5fb8f5b100d7284ba01838a01c`
- DVC: `data/prepared.dvc`
- MLflow run: `69f2df8e614b4efc8cea9ea98e442368`
- Umbral: `0.50`

## Referencia

Moustafa, N. y Slay, J. *UNSW-NB15: a comprehensive data set for network
intrusion detection systems*. Fuente oficial: UNSW-NB15, UNSW Canberra.
