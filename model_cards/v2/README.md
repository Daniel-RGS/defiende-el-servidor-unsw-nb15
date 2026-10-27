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
recall con FPR máximo de 0.05. Test no se usó.

El artefacto se distribuye en formato `joblib`; cárguelo únicamente desde esta
revisión verificada y no desde archivos joblib de procedencia desconocida.

## Validación

Con umbral 0.51: recall ataque 0.9463; precision ataque 0.9762; FPR 0.0490;
macro-F1 0.9410. Matriz de confusión: `[[10801, 557], [1296, 22837]]`.

## Limitaciones y uso

El margen frente al FPR máximo es pequeño y puede cambiar en test por cambio de
distribución y solapamiento. La validación pesa cada fila, incluidas
repeticiones. El dataset es histórico y no demuestra eficacia sobre redes
actuales. No usar `attack_cat` como entrada.

## Trazabilidad

- Git commit del código: `7c35ad5b8734ab5fb8f5b100d7284ba01838a01c`
- DVC: `data/prepared.dvc`
- MLflow run: `dcdbd1d174e442039826cfb6d38ccb99`
- Criterio: `evidencias/criterio-seleccion.json`
- Umbral: `0.51`

## Referencia

Moustafa, N. y Slay, J. *UNSW-NB15: a comprehensive data set for network
intrusion detection systems*. Fuente oficial: UNSW-NB15, UNSW Canberra.
