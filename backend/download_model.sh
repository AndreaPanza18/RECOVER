#!/usr/bin/env bash
set -e
set -u

MODEL_DIR="/app/models"
MODEL_FILE="llama-2-7b-chat.Q4_K_M.gguf"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"

# 1. assicuriamoci che la directory esista
mkdir -p "${MODEL_DIR}"

# 2. se il modello non c’è, lo scarichiamo
if [[ ! -f "${MODEL_PATH}" ]]; then
  echo "[startup] modello non trovato → download..."
  if [[ -z "${LLM_MODEL_URL:-}" ]]; then
    echo "LLM_MODEL_URL non definita! Esci." >&2
    exit 1
  fi
  curl -L --progress-bar "${LLM_MODEL_URL}" -o "${MODEL_PATH}"
else
  echo "[startup] modello presente → skip download"
fi

# 3. avvia l’app FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000
