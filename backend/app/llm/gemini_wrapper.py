import os
import google.generativeai as genai
from app.llm.cache import _cache_key, load_from_cache, save_to_cache

def build_genai_wrapper():

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY non configurata!")

    genai.configure(api_key=api_key)

    model_name = os.getenv("GENAI_MODEL", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name)

    def run(prompt: str, **kwargs):
        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 512),
            "stop": kwargs.get("stop", None),
        }

        # ========================================================
        # CACHE CHECK
        # ========================================================

        key = _cache_key("genai", prompt, params)
        cached = load_from_cache(key)
        if cached:
            return cached

        # ========================================================
        # GEMINI CALL
        # ========================================================

        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": params["temperature"],
                    "max_output_tokens": params["max_tokens"],
                    "stop_sequences": params["stop"],
                },
            )

            text = getattr(response, "text", "")
            text = text.strip() if text else ""

            out = {"choices": [{"text": text}]}

            save_to_cache(key, out)
            return out

        except Exception as e:
            # NON lanciare eccezione → safe_call gestisce fallback
            return {"choices": [{"text": f"[ERRORE GEMINI] {str(e)}"}]}

    return run
