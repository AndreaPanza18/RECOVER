import os
from openai import OpenAI
from app.llm.cache import _cache_key, load_from_cache, save_to_cache

def build_openai_wrapper():

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY non configurata!")

    client = OpenAI(api_key=api_key)
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def run(prompt: str, **kwargs):
        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 512),
            "stop": kwargs.get("stop", None),
        }

        # ========================================================
        # CACHE CHECK
        # ========================================================

        key = _cache_key("openai", prompt, params)
        cached = load_from_cache(key)
        if cached:
            return cached

        # ========================================================
        # OPENAI CALL
        # ========================================================

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=params["temperature"],
                max_tokens=params["max_tokens"],
                stop=params["stop"],
            )

            text = response.choices[0].message.content.strip()

            # Normalizza output per compatibilità con Gemini/LLaMA
            out = {"choices": [{"text": text}]}

            save_to_cache(key, out)
            return out

        except Exception as e:
            # NON lanciare eccezione → safe_call gestisce fallback
            return {"choices": [{"text": f"[ERRORE OPENAI] {str(e)}"}]}

    return run
