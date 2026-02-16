import os

# ============================================================
# DIRECTORY GLOBALI
# ============================================================

BASE_DIR = "/app"
MODEL_DIR = os.path.join(BASE_DIR, "models")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# Crea cache se non esiste
os.makedirs(CACHE_DIR, exist_ok=True)

print(f"MODEL_DIR = {MODEL_DIR}")
print(f"CACHE_DIR = {CACHE_DIR}")

