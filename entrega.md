# Índice de evidencias

- Repositorio: https://github.com/Daniel-RGS/defiende-el-servidor-unsw-nb15
- Commit actual de entrega: consultar `git rev-parse HEAD`.
- Datos originales: `data/raw/*.dvc`, con remote DVC configurado en `.dvc/config`.
- Datos preparados y splits: `data/prepared.dvc`.
- Auditoría: `evidencias/auditoria.json`.
- Diccionario de variables: `evidencias/diccionario_variables.json`.
- Recuperación sin credenciales: `evidencias/recuperacion/dvc-pull-sin-credenciales.log`.
- Recuperación de datos preparados: `evidencias/recuperacion/dvc-prepared-pull.log`.

## Política de acceso DVC

El remote DVC requiere autenticación. El log de recuperación sin credenciales
documenta explícitamente el fallo `Unable to locate credentials`; no se incluyen
tokens en Git ni en el ZIP. Para una recuperación docente se debe otorgar acceso
al repositorio/remote en DagsHub o entregar por separado un respaldo del
almacenamiento DVC, según el mecanismo acordado con el docente.

## Splits

La asignación reproducible está dentro de `data/prepared.dvc` en
`split_assignments.csv`. Se usó la semilla `20261027`, validación del 20% y
agrupación por la representación de todas las variables predictoras. El número
de grupos idénticos compartidos entre train y validación es cero.

## Transformación de datos preparados

La versión preparada conserva las 45 columnas originales para auditoría y
trazabilidad, pero materializa dos subconjuntos derivados únicamente del archivo
de entrenamiento: `train.csv` (139.850 filas) y `validation.csv` (35.491 filas).
También conserva `split_assignments.csv` y las referencias por fila. El archivo
de test no se modifica ni se usa para construir los splits; solo se audita para
esquema, duplicados y solapamiento por variables predictoras.

