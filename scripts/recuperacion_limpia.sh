#!/usr/bin/env bash
# Prueba de recuperación en una carpeta y un entorno nuevos, sin cachés previas de datos ni modelos.
# Uso: bash scripts/recuperacion_limpia.sh <commit-o-tag> [carpeta-nueva] 2>&1 | tee recuperacion.log
set -euo pipefail

REVISION="${1:?Uso: scripts/recuperacion_limpia.sh <commit-o-tag> [carpeta-nueva]}"
WORK="${2:-$(mktemp -d)}"
REPO_URL="${REPO_URL:-https://github.com/Daniel-RGS/defiende-el-servidor-unsw-nb15.git}"
PYTHON="${PYTHON:-python3.12}"
DRIVE_ID="1j7H_eR0oXREf799NVNKJ-N3yUl-Lag4b"
BACKUP_SHA256="9a8e05590a0d41110051662b956ca78455919968a86f2ee6cdd6a8fc193e620d"

if [ -e "$WORK" ] && [ -n "$(ls -A "$WORK")" ]; then echo "La carpeta $WORK no está vacía" >&2; exit 1; fi
mkdir -p "$WORK"; WORK="$(cd "$WORK" && pwd)"
export HF_HOME="$WORK/hf-home"   # caché de Hugging Face nueva y vacía
sha() { if command -v sha256sum >/dev/null; then sha256sum "$@"; else shasum -a 256 "$@"; fi; }
run() { echo "\$ $*"; "$@"; }
check() { local got; got="$(sha "$2" | cut -d' ' -f1)"; if [ "$got" = "$1" ]; then echo "OK  $got  $2"; else echo "FALLA  $got  $2 (esperado $1)"; exit 1; fi; }
phase() { echo; echo "## $1 (t=${SECONDS}s)"; }

phase "Entorno"
date -u +"inicio UTC: %Y-%m-%dT%H:%M:%SZ"
uname -sm
if command -v sysctl >/dev/null; then sysctl -n machdep.cpu.brand_string 2>/dev/null || true; echo "RAM bytes: $(sysctl -n hw.memsize 2>/dev/null || echo n/d)"; fi
echo "carpeta nueva: $WORK"

phase "1. Código en la revisión elegida y dependencias fijadas"
cd "$WORK"
run git clone --quiet "$REPO_URL" proyecto
cd proyecto
run git checkout --quiet "$REVISION"
run git rev-parse HEAD
run "$PYTHON" -m venv .venv
source .venv/bin/activate
run python --version
run pip install --quiet --disable-pip-version-check --upgrade pip
REQS=requirements.txt
if [ "$(uname -sm)" = "Darwin x86_64" ]; then
  # cryptography 50.0.2 no publica rueda para Mac Intel; 48.0.1 es la última que sí. No interviene en datos ni modelos.
  echo "NOTA: Mac Intel, se sustituye cryptography==50.0.2 por cryptography==48.0.1"
  REQS="$WORK/requirements-mac-intel.txt"
  sed 's/^cryptography==50.0.2$/cryptography==48.0.1/' requirements.txt > "$REQS"
fi
run pip install --quiet --disable-pip-version-check -r "$REQS"
run pip check
run pip install --quiet --disable-pip-version-check gdown==5.2.0

phase "2. Datos con DVC desde el respaldo entregado en Drive"
run gdown --quiet "$DRIVE_ID" --output "$WORK/dvc-storage.tar.gz"
check "$BACKUP_SHA256" "$WORK/dvc-storage.tar.gz"
run tar -xzf "$WORK/dvc-storage.tar.gz" -C "$WORK"
run dvc remote add --local backup "$WORK/cache"
run dvc pull -r backup
check bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa data/raw/UNSW_NB15_training-set.csv
check 734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559 data/raw/UNSW_NB15_testing-set.csv
check 8a6538f6423a503e76cdf82ebbbf73c1449689d27388de4e1e34a3abf8eded8c data/prepared/split_assignments.csv
check ca485acb8f9857cd160a6412bf67c8163aa8ee29c0a71150dff5cff089a5c8a3 data/prepared/train_rows.csv
check 385223116b73b87ec56b1460ce0b1d3d121e9af3480f71bc4bc31a59b17f04e4 data/prepared/validation_rows.csv
run dvc status

phase "3 a 5. Modelos v1 y v2 desde Hugging Face por SHA y comparación de predicciones"
run python -m src.recover --output-dir "$WORK/salidas" --download-dir "$WORK/modelos-hf"
sha "$WORK"/modelos-hf/v1/pipeline.joblib "$WORK"/modelos-hf/v2/pipeline.joblib evidencias/recuperacion/entrada-validacion-20.csv

phase "Fin"
date -u +"fin UTC: %Y-%m-%dT%H:%M:%SZ"
echo "duración total: ${SECONDS}s"
echo "RESULTADO: recuperación correcta"
