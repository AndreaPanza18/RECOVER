import os
from llama_cpp import Llama
from app.utils.env_loader import MODEL_DIR
from app.llm.cache import _cache_key, load_from_cache, save_to_cache

def build_llama_wrapper():

    model_file = os.getenv("LLM_MODEL_FILE", "llama-2-7b-chat.Q4_K_M.gguf")
    model_path = os.path.join(MODEL_DIR, model_file)

    if not os.path.exists(model_path):
        raise RuntimeError(f"Modello LLaMA non trovato: {model_path}")

    # Caricamento modello UNA sola volta
    llama = Llama(
        model_path=model_path,
        n_ctx=int(os.getenv("LLAMA_CTX", 2048)),
        n_threads=int(os.getenv("LLAMA_THREADS", 4)),
        verbose=False,
    )

    def run(prompt: str, **kwargs):
        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 512),
            "stop": kwargs.get("stop", None),
        }

        # ========================================================
        # CACHE CHECK
        # ========================================================

        key = _cache_key("llama", prompt, params)
        cached = load_from_cache(key)
        if cached:
            return cached

        # ========================================================
        # LLAMA CALL
        # ========================================================

        try:
            result = llama.create_completion(
                prompt,
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
                stop=params["stop"],
            )

            text = result["choices"][0]["text"].strip()

            out = {"choices": [{"text": text}]}
            save_to_cache(key, out)
            return out

        except Exception as e:
            # LLaMA è il fallback finale → non rilanciare
            return {"choices": [{"text": f"[ERRORE LLAMA] {str(e)}"}]}

    return run
