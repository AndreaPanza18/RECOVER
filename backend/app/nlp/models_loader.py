import os
import pickle
import fasttext
import nltk
from app.utils.env_loader import MODEL_DIR
from app.nlp.dialog_tag import DialogTag

try:
    print("Looking for NLTK punkt tokenizer...")
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("⚠️ Download NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=True)

# ============================================================
# CARICAMENTO MODELLI
# ============================================================

FASTTEXT_MODEL_PATH = os.path.join(MODEL_DIR, "fasttext_model.bin")
if not os.path.exists(FASTTEXT_MODEL_PATH):
    raise FileNotFoundError(f"fastText model non trovato: {FASTTEXT_MODEL_PATH}")

ft_model = fasttext.load_model(FASTTEXT_MODEL_PATH)

dialog_tagger = DialogTag('bert-base-uncased')

PICKLE_MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
if not os.path.exists(PICKLE_MODEL_PATH):
    raise FileNotFoundError(f"Pickle model non trovato: {PICKLE_MODEL_PATH}")

with open(PICKLE_MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
