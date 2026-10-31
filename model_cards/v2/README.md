---
library_name: scikit-learn
tags:
- network-intrusion-detection
- unsw-nb15
---

# Defiende el servidor — v2

## Propósito

Clasificación binaria de flujos UNSW-NB15: `0` normal y `1` ataque.

## Modelo y datos

Random forest balanceado de 100 árboles, `max_depth=18`, dentro de un único
pipeline scikit-learn. El preprocesamiento imputa, codifica `proto`, `service`,
`state` con one-hot y escala las variables numéricas. Las columnas `id`,
`attack_cat` y `label` no entran al modelo. El umbral congelado es `0.51`.

Se usaron los splits fijos de `data/prepared.dvc`, semilla `20261027`, y el
barrido de umbrales se hizo solo sobre validación. El criterio fue maximizar
recall con FPR máximo de 0.05. La evaluación final se hizo una sola vez sobre
el test congelado, sin reajustar el umbral.

El artefacto se distribuye en formato `joblib`; cárguelo únicamente desde esta
revisión verificada y no desde archivos joblib de procedencia desconocida.

## Validación

Con umbral 0.51: recall ataque 0.9463; precision ataque 0.9762; FPR 0.0490;
macro-F1 0.9410. Matriz de confusión: `[[10801, 557], [1296, 22837]]`.

## Limitaciones y uso

El margen frente al FPR máximo es pequeño y puede cambiar en test por cambio de
distribución y solapamiento. La validación pesa cada fila, incluidas
repeticiones. En el test, el FPR fue 0.1626, por encima del 0.05 observado en
validación; este resultado se conserva como limitación. El dataset es histórico
y no demuestra eficacia sobre redes actuales. Es un ejercicio académico y no
está validado para una red real. No usar `attack_cat` como entrada.

## Test congelado

Se evaluó la revisión HF `d71ac6a63d9a80ecc7af6c13601676a71b925da3` con umbral
0.51 sobre 82.332 filas. Recall ataque: 0.9649; precision ataque: 0.8791;
FPR: 0.1626; macro-F1: 0.9053; accuracy: 0.9076. Matriz de confusión:
`[[30983, 6017], [1591, 43741]]`.

El SHA-256 de `pipeline.joblib` es
`5c18730460aadd105d0cd762165edb66ad2fcfec5afa89fbc1098eda83f74342`, igual al
artefacto publicado y al modelo evaluado.

## Trazabilidad

- Git commit del código: `7c35ad5b8734ab5fb8f5b100d7284ba01838a01c`
- DVC: `data/prepared.dvc`
- MLflow run: `dcdbd1d174e442039826cfb6d38ccb99`
- Criterio: `evidencias/criterio-seleccion.json`
- Umbral: `0.51`

## Referencia

Moustafa, N. y Slay, J. *UNSW-NB15: a comprehensive data set for network
intrusion detection systems*. Fuente oficial: UNSW-NB15, UNSW Canberra.
