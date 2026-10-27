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
- Análisis de sensibilidad: se añadirá después de ejecutar los modelos, usando las predicciones de validación y excluyendo los 940 registros contradictorios.

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

