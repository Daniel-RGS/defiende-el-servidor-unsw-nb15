# Índice de evidencias

- Repositorio: https://github.com/Daniel-RGS/defiende-el-servidor-unsw-nb15
- Commit actual de entrega: consultar `git rev-parse HEAD`.
- Datos originales: `data/raw/*.dvc`, con remote DVC configurado en `.dvc/config`.
- Datos preparados y splits: `data/prepared.dvc`.
- Auditoría: `evidencias/auditoria.json`.
- Diccionario de variables: `evidencias/diccionario_variables.json`.
- Recuperación sin credenciales: `evidencias/recuperacion/dvc-pull-sin-credenciales.log`.
- Recuperación de datos preparados: `evidencias/recuperacion/dvc-prepared-pull.log`.
- Prueba del remote HTTPS público sin credenciales: `evidencias/recuperacion/dvc-pull-public-https-sin-credenciales.log`.
- Recuperación desde respaldo Drive: `evidencias/recuperacion/dvc-pull-drive.log`.
- Análisis de sensibilidad: `evidencias/metricas-sensibilidad.csv` y `.json`, usando las predicciones de validación y excluyendo los 940 registros contradictorios cuando pertenecen a validación.
- Tabla de corridas: `evidencias/experimentos.csv`.
- Sensibilidad sin grupos contradictorios: `evidencias/metricas-sensibilidad.csv` y `.json`.
- Exportación estructurada de MLflow: `evidencias/mlflow/<run_id>/`.
- Criterio y selección de umbral: `evidencias/criterio-seleccion.json`, `evidencias/umbral-sweep-all.csv`, `evidencias/umbral-candidatos.csv`, `evidencias/seleccion-umbral.json` y `evidencias/seleccion.json`.
- Recuperación de v1/v2 desde Hugging Face: `evidencias/recuperacion/hf-recovery.log`.

## Política de acceso DVC

El remote DVC requiere autenticación. El log de recuperación sin credenciales
documenta explícitamente el fallo `Unable to locate credentials`; no se incluyen
tokens en Git ni en el ZIP. Para una recuperación docente se debe otorgar acceso
al repositorio/remote en DagsHub o entregar por separado un respaldo del
almacenamiento DVC, según el mecanismo acordado con el docente.

La prueba del endpoint HTTPS `.dvc` sin credenciales tampoco recuperó los objetos:
el endpoint fue accesible, pero reportó tres objetos ausentes en el remote. Por
tanto, el acceso público no es suficiente para esta entrega.

Respaldo separado preparado para Drive (no se incluye en Git ni en el ZIP):
`backups/defiende-servidor-dvc-storage-2026-10-27.tar.gz`, SHA-256
`9a8e05590a0d41110051662b956ca78455919968a86f2ee6cdd6a8fc193e620d`.
Enlace público: https://drive.google.com/file/d/1j7H_eR0oXREf799NVNKJ-N3yUl-Lag4b/view?usp=drive_link
La prueba limpia descargó el archivo con `gdown`, verificó ese SHA-256, lo
extrajo y recuperó tanto los CSV originales como los datos preparados.
Contiene `.dvc/cache`; para usarlo como remote local, extraerlo y ejecutar:

```bash
dvc remote add backup /ruta/al/cache-extraido
dvc pull -r backup
```

## Splits

La asignación reproducible está dentro de `data/prepared.dvc` en
`split_assignments.csv`. Se usó la semilla `20261027`, validación del 20% y
agrupación por la representación de todas las variables predictoras. El número
de grupos idénticos compartidos entre train y validación es cero.

La llave de agrupación usa exactamente las 42 variables predictoras: todas las
columnas excepto `id`, `label` y `attack_cat`. Hay 9.748 grupos con más de una
fila, que involucran 74.301 filas duplicadas más allá de la primera aparición.
Hay 229 grupos con etiquetas contradictorias (940 filas involucradas). Se
conservan y se asignan completos a una sola partición; se marcan para análisis,
no se resuelven por mayoría ni se eliminan, porque eliminar o relabelar datos
alteraría artificialmente la distribución y la comparación. Al no partirlos,
la política no introduce fuga entre train y validación.

El test se auditó solo con las predictoras: 6.886 filas solapan grupos de train
y 1.655 grupos de validación; no se usaron etiquetas de test para ninguna
decisión.

Esto equivale a 8,36% del test con grupos de train y 2,01% con grupos de
validación; el solapamiento total por grupo es aproximadamente 10,37%. Las
métricas del test se interpretarán con esta limitación, porque el solapamiento
puede favorecerlas.

El criterio se fijó el 27 de octubre de 2026 antes de seleccionar v2:
maximizar recall de ataque con FPR máximo de 5%; en empates, macro-F1 y luego
precision. El barrido de validación eligió random forest con umbral 0,51:
recall 0,9463, precision 0,9762, FPR 0,0490 y macro-F1 0,9410. v1 es la
logística baseline con umbral 0,50; v2 es el bosque balanceado de 100 árboles
con umbral 0,51. La comparación no usa test.

El criterio se redactó después de observar las métricas iniciales a umbral 0,5,
pero antes del barrido de umbrales; esta secuencia queda visible en el historial
Git. El barrido aplicó exactamente la misma rejilla a las seis corridas. Random
forest obtuvo el mayor recall factible (0,9463 con FPR 0,0490); el siguiente fue
árbol balanceado (0,9291 con FPR 0,0458).

El margen de v2 respecto al límite de FPR es pequeño (0,0490 frente a 0,05).
El umbral 0,51 puede no conservar ese límite en test por cambio de distribución
y por el solapamiento auditado del test; si ocurre, se reportará sin reajustar.

Hugging Face: repositorio `Daniel-RGS/defiende-el-servidor-unsw-nb15`.
La revisión v1 es `c4ed6901110c506b99438df76933c779fc9e737c` y la revisión v2 es
`d71ac6a63d9a80ecc7af6c13601676a71b925da3`. Ambas fueron descargadas por SHA
en una carpeta limpia y sus predicciones coincidieron con las locales sobre 20
filas fijas de validación; la diferencia máxima de score fue 0 para v1 y
1,11e-16 para v2.

Las métricas se calcularán por fila, incluyendo repeticiones: esto da mayor peso
a los patrones frecuentes y es coherente con la unidad de observación publicada.
Además se reportará un análisis de sensibilidad sobre validación excluyendo los
940 registros pertenecientes a grupos con etiquetas contradictorias. Dos filas
idénticas con etiquetas opuestas no pueden ser acertadas simultáneamente por un
modelo determinista, por lo que esos grupos imponen un techo práctico a las
métricas.

Las fuentes, fechas UTC de descarga, SHA-256, tipos, faltantes y clases de ambos
archivos están en `evidencias/auditoria.json`.

## Declaración de herramientas y contribuciones

Se utilizó Codex como asistente de IA para apoyar la organización del repositorio,
la escritura de scripts de auditoría, la configuración reproducible de DVC y la
revisión de comandos. Daniel verificó los SHA-256, filas, columnas, tipos,
faltantes, duplicados, contradicciones, asignación por grupos, configuración sin
secretos y recuperaciones desde carpetas limpias. La interpretación final de las
métricas y la defensa de las decisiones corresponden a los integrantes.

## Transformación de datos preparados

La versión preparada conserva las 45 columnas originales para auditoría y
trazabilidad, pero materializa dos subconjuntos derivados únicamente del archivo
de entrenamiento: `train.csv` (139.850 filas) y `validation.csv` (35.491 filas).
También conserva `split_assignments.csv` y las referencias por fila. El archivo
de test no se modifica ni se usa para construir los splits; solo se audita para
esquema, duplicados y solapamiento por variables predictoras.

