#!/usr/bin/env bash
# Arma el ZIP de entrega desde un commit de Git: solo archivos versionados, sin datos, entornos, cachés ni credenciales.
# Uso: bash scripts/empaquetar_entrega.sh <tag-o-commit> <carpeta-salida>
set -euo pipefail

REV="${1:?Uso: scripts/empaquetar_entrega.sh <tag-o-commit> <carpeta-salida>}"
OUT="${2:?Uso: scripts/empaquetar_entrega.sh <tag-o-commit> <carpeta-salida>}"
SHA="$(git rev-parse "$REV^{commit}")"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT

git archive --format=tar --prefix=proyecto/ "$SHA" | tar -x -C "$STAGE"
printf '%s\n' "$SHA" > "$STAGE/proyecto/COMMIT_ENTREGA.txt"
rm -f "$OUT/defiende-el-servidor-proyecto.zip"
(cd "$STAGE" && zip -qrX "$OUT/defiende-el-servidor-proyecto.zip" proyecto)

# Comprobaciones: nada prohibido dentro del ZIP.
LIST="$(unzip -Z1 "$OUT/defiende-el-servidor-proyecto.zip")"
if grep -nE '(^|/)(\.venv|venv|mlruns|__pycache__|\.dvc/cache|\.dvc/tmp|backups|modelos-hf|reproduccion)/|\.env$|config\.local$|\.joblib$|UNSW_NB15_.*\.csv$|dvc-storage' <<<"$LIST"; then
  echo "ERROR: el ZIP contiene archivos que no deben entregarse" >&2; exit 1
fi
if unzip -p "$OUT/defiende-el-servidor-proyecto.zip" | grep -aEq 'hf_[A-Za-z0-9]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}'; then
  echo "ERROR: posible token dentro del ZIP" >&2; exit 1
fi
echo "commit: $SHA"
echo "archivos: $(wc -l <<<"$LIST" | tr -d ' ')"
ls -l "$OUT/defiende-el-servidor-proyecto.zip"
if command -v sha256sum >/dev/null; then sha256sum "$OUT/defiende-el-servidor-proyecto.zip"; else shasum -a 256 "$OUT/defiende-el-servidor-proyecto.zip"; fi
