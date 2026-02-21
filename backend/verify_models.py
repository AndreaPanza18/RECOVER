import os
import sys

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

REQUIRED = [
    "fasttext_model.bin",
    "llama-2-7b-chat.Q4_K_M.gguf",
    "model.pkl"
]

missing = [
    m for m in REQUIRED
    if not os.path.exists(os.path.join(MODELS_DIR, m))
]

if missing:
    print("\nModelli mancanti:")
    for m in missing:
        print(" -", m)
    print("\nEsegui dalla root:")
    print("  python install.py\n")
    sys.exit(1)
