#!/bin/bash
set -e

echo "🔎 Verifica modelli..."

python install.py

echo "🚀 Avvio backend..."

exec uvicorn main:app --host 0.0.0.0 --port 8000