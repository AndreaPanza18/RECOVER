from app.llm.openai_wrapper import build_openai_wrapper
from app.llm.gemini_wrapper import build_genai_wrapper
from app.llm.llama_wrapper import build_llama_wrapper

_current_provider = None
_llm_instance = None

def get_llm(provider: str):

    global _current_provider, _llm_instance

    # Se cambio provider, resetto istanza
    if provider != _current_provider:
        _current_provider = provider
        _llm_instance = None

    # Se non istanziato → crea wrapper
    if _llm_instance is None:
        if provider == "chatgpt":
            _llm_instance = build_openai_wrapper()
        elif provider == "genai":
            _llm_instance = build_genai_wrapper()
        else:
            # fallback LLaMA
            _llm_instance = build_llama_wrapper()

    return _llm_instance
