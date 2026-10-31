# Recuperación final en entorno nuevo (30 de octubre de 2026)

- Comando: `bash scripts/recuperacion_limpia.sh d030aad1fb53ddb069d28f0fa1c5f00e538183b6 <carpeta-nueva>`
- Log completo y sin editar: `recuperacion-limpia.log`.
- Entrada fija: `../entrada-validacion-20.csv` (20 filas de validación, SHA-256 `9bd7bb2451eb41403a61bc8b0bea01d880d9ee63958d6a5dd0d075dc59c4d7a5`).
- Salidas antes de publicar: `../v1-predictions-before-hf.csv` y `../v2-predictions-before-hf.csv`.
- Salidas después de recuperar: `v1-predictions-after-recovery.csv` y `v2-predictions-after-recovery.csv`.
- Comparación con tolerancia `1e-12`: `comparacion.json`. Diferencia máxima 0 en v1 y 2,22e-16 en v2; etiquetas iguales en las 20 filas de ambas versiones.
- Hashes verificados: respaldo DVC, CSV originales, splits preparados y `pipeline.joblib` de v1 y v2 (ver log).
- Carpeta, entorno virtual, caché DVC y caché de Hugging Face nuevos. La caché de paquetes de pip sí se reutilizó, por eso la instalación tomó solo 143 s.
- Equipo: Mac Intel Core i3-1000NG4, 8 GB de RAM, Python 3.12.14. Duración total: 175 s.
