from app.llm.provider import get_llm

_FALLBACK_ACTIVE = False

def safe_llm_call(provider: str, prompt: str, **kwargs) -> str:

    global _FALLBACK_ACTIVE

    # Se fallback già attivo → forza LLaMA
    if _FALLBACK_ACTIVE:
        return get_llm("llama")(prompt, **kwargs)["choices"][0]["text"].strip()

    try:
        llm = get_llm(provider)
        resp = llm(prompt, **kwargs)
        text = resp["choices"][0]["text"].strip()

        # Controllo errori
        if not text:
            raise RuntimeError(f"LLM {provider} ha restituito testo vuoto")

        if "[errore openai]" in text.lower() or "[errore gemini]" in text.lower():
            raise RuntimeError(f"LLM {provider} non disponibile o quota superata")

        return text

    except Exception as e:
        # --- sticky fallback: attiva LLaMA per tutte le chiamate future ---
        print(f"⚠️ Fallback LLaMA attivato definitivamente per {provider}: {e}")
        _FALLBACK_ACTIVE = True
        return get_llm("llama")(prompt, **kwargs)["choices"][0]["text"].strip()


# ============================================================
# RESET FALLBACK
# ============================================================

def reset_fallback():
    global _FALLBACK_ACTIVE
    _FALLBACK_ACTIVE = False


# ============================================================
# WRAPPER HELPER UNIVERSALE
# ============================================================

def ask(provider: str, prompt: str, **kwargs) -> str:
    return safe_llm_call(provider, prompt, **kwargs)
