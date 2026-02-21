import os
import sys
import time
import requests
import gdown
from tqdm import tqdm

MODELS_DIR = os.path.join("models")

RETRY_COUNT = 3
CHUNK_SIZE = 1024 * 1024
TIMEOUT = 30

MODELS = {
    "fasttext_model.bin": {
        "size": 804_948_004,
        "hf": "https://huggingface.co/AndreaPanza18/RECOVER-models/resolve/main/fasttext_model.bin",
        "drive": "https://drive.google.com/uc?id=1Gmp_UrwFgCtGwJBQaQd9nqV-BOd642AC"
    },
    "llama-2-7b-chat.Q4_K_M.gguf": {
        "size": 4_081_004_224,
        "hf": "https://huggingface.co/AndreaPanza18/RECOVER-models/resolve/main/llama-2-7b-chat.Q4_K_M.gguf",
        "drive": "https://drive.google.com/uc?id=1Bzk8AZhG5FLAVTjlTMAcSLB8JyHLEx_P"
    },
    "model.pkl": {
        "size": 5_609_800,
        "hf": "https://huggingface.co/AndreaPanza18/RECOVER-models/resolve/main/model.pkl",
        "drive": "https://drive.google.com/uc?id=1RCWGSJSuKu_4MVJlSWUjAs61sMDfKTsA"
    }
}


def download_with_requests(url, path, expected_size=None):
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            with requests.get(url, stream=True, timeout=TIMEOUT) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                total = expected_size if expected_size else total
                with open(path, 'wb') as f, tqdm(
                    total=total, unit='B', unit_scale=True, desc=os.path.basename(path)
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            if expected_size and os.path.getsize(path) != expected_size:
                raise Exception(f"File scaricato corrotto: {os.path.getsize(path)} != {expected_size}")
            return True
        except Exception as e:
            print(f"[Tentativo {attempt}/{RETRY_COUNT}] Errore download: {e}")
            if os.path.exists(path):
                os.remove(path)
            time.sleep(2)
    return False


def download_hf(url, path, expected_size=None):
    print("🌐 Tentativo download da HuggingFace...")
    return download_with_requests(url, path, expected_size)


def download_drive(url, path, expected_size=None):
    print("📥 Tentativo download da Google Drive...")
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            gdown.download(url, path, quiet=False, resume=True)
            if expected_size and os.path.getsize(path) != expected_size:
                raise Exception(f"File Drive corrotto: {os.path.getsize(path)} != {expected_size}")
            return True
        except Exception as e:
            print(f"[Tentativo {attempt}/{RETRY_COUNT}] Errore Drive: {e}")
            if os.path.exists(path):
                os.remove(path)
            time.sleep(2)
    return False


def download_model(name, cfg):
    path = os.path.join(MODELS_DIR, name)

    # Se già presente e corretto → OK
    if os.path.exists(path) and os.path.getsize(path) == cfg["size"]:
        print(f"{name} già presente ✓")
        return True

    if os.path.exists(path):
        print(f"{name} corrotto. Rimuovo e riscarico...")
        os.remove(path)

    # --- Tentativo HuggingFace ---
    if download_hf(cfg["hf"], path, cfg["size"]):
        print(f"{name} scaricato correttamente da HuggingFace ✓")
        return True

    print(f"HuggingFace fallito, provo Google Drive...")

    # --- Fallback Drive ---
    if download_drive(cfg["drive"], path, cfg["size"]):
        print(f"{name} scaricato correttamente da Google Drive ✓")
        return True

    print(f"❌ Download fallito per {name}")
    return False


def main():
    print("\n=== INSTALLAZIONE MODELLI RECOVER ===\n")

    os.makedirs(MODELS_DIR, exist_ok=True)

    for name, cfg in MODELS.items():
        print(f"\n--- {name} ---")
        if not download_model(name, cfg):
            print(f"\nErrore download {name}. Esco.")
            sys.exit(1)

    print("\n✅ Tutti i modelli installati correttamente!")


if __name__ == "__main__":
    main()