import pickle
import os
import fasttext
import pandas as pd
import nltk
import json
import hashlib
from dialog_tag import DialogTag
from llama_cpp import Llama
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Carica .env solo per API_KEY e MODEL_NAME
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# ================================================================
# CARICAMENTO VARIABILI D'AMBIENTE
# ================================================================
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

MODEL_DIR = "models/"
CACHE_DIR = "cache/"
os.makedirs(CACHE_DIR, exist_ok=True)

# ================================================================
# CACHE SYSTEM
# ================================================================
def _cache_key(provider: str, prompt: str, params: dict) -> str:
    raw = provider + prompt + json.dumps(params, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")

def load_from_cache(key: str):
    path = _cache_path(key)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf8") as f:
                return json.load(f)
        except:
            return None
    return None

def save_to_cache(key: str, content: dict):
    path = _cache_path(key)
    try:
        with open(path, "w", encoding="utf8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    except:
        pass

# ================================================================
# WRAPPER CHATGPT
# ================================================================
def build_openai_wrapper():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY non configurata!")

    client = OpenAI(api_key=api_key)
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def run(prompt, **kwargs):
        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 512),
            "stop": kwargs.get("stop", None),
        }

        # ---- CACHE CHECK ----
        key = _cache_key("openai", prompt, params)
        cached = load_from_cache(key)
        if cached:
            return cached

        # ---- CALL CHAT GPT ----
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
                stop=params["stop"],
            )

            text = response.choices[0].message.content.strip()

            out = {"choices": [{"text": text}]}
            save_to_cache(key, out)
            return out

        except Exception as e:
            return {"choices": [{"text": f"[ERRORE OPENAI] {str(e)}"}]}

    return run


# ================================================================
# WRAPPER GEMINI
# ================================================================
def build_genai_wrapper():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY non configurata!")

    genai.configure(api_key=api_key)
    model_name = os.getenv("GENAI_MODEL", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name)

    def run(prompt, **kwargs):
        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 512),
            "stop": kwargs.get("stop", None),
        }

        # ---- CACHE CHECK ----
        key = _cache_key("genai", prompt, params)
        cached = load_from_cache(key)
        if cached:
            return cached

        # ---- CALL GEMINI ----
        try:
            resp = model.generate_content(
                prompt,
                generation_config={
                    "temperature": params["temperature"],
                    "max_output_tokens": params["max_tokens"],
                    "stop_sequences": params["stop"],
                },
            )

            text = getattr(resp, "text", "").strip()
            out = {"choices": [{"text": text}]}
            save_to_cache(key, out)
            return out

        except Exception as e:
            return {"choices": [{"text": f"[ERRORE GEMINI] {str(e)}"}]}

    return run

# ================================================================
# WRAPPER LLAMA
# ================================================================
def build_llama_wrapper():
    model_file = os.getenv("LLM_MODEL_FILE", "llama-2-7b-chat.Q4_K_M.gguf")
    model_path = os.path.join(MODEL_DIR, model_file)
    if not os.path.exists(model_path):
        raise RuntimeError(f"Modello Llama non trovato: {model_path}")

    llama = Llama(
        model_path=model_path,
        n_ctx=int(os.getenv("LLAMA_CTX", 2048)),
        n_threads=int(os.getenv("LLAMA_THREADS", 4)),
        verbose=False,
    )

    def run(prompt, **kwargs):
        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 512),
            "stop": kwargs.get("stop", None),
        }

        key = _cache_key("llama", prompt, params)
        cached = load_from_cache(key)
        if cached:
            return cached

        try:
            result = llama.create_completion(
                prompt,
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
                stop=params["stop"]
            )
            text = result["choices"][0]["text"].strip()
            out = {"choices": [{"text": text}]}
            save_to_cache(key, out)
            return out
        except Exception as e:
            return {"choices": [{"text": f"[ERRORE LLAMA] {str(e)}"}]}

    return run

# ================================================================
# GESTIONE PROVIDER
# ================================================================
_current_provider = None
_llm_instance = None

def get_llm(provider: str):
    global _current_provider, _llm_instance
    if provider != _current_provider:
        _current_provider = provider
        _llm_instance = None

    if _llm_instance is None:
        if provider == "genai":
            _llm_instance = build_genai_wrapper()
        elif provider == "chatgpt":
            _llm_instance = build_openai_wrapper()
        else:
            _llm_instance = build_llama_wrapper()

    return _llm_instance

# ================================================================
# WRAPPER UNIVERSALE CON FALLBACK SU LLAMA
# ================================================================

_FALLBACK_ACTIVE = False

def safe_llm_call(provider: str, prompt: str, **kwargs) -> str:
    """
    Richiama il LLM specificato e, in caso di errore o superamento quota,
    passa definitivamente a LLaMA per tutte le chiamate successive.
    """
    global _FALLBACK_ACTIVE

    # Se il fallback è già attivo, forza LLaMA
    if _FALLBACK_ACTIVE:
        llama_resp = get_llm("llama")(prompt, **kwargs)
        return llama_resp["choices"][0]["text"].strip()

    try:
        llm = get_llm(provider)
        resp = llm(prompt, **kwargs)
        text = resp["choices"][0]["text"].strip()

        # --- Controllo errori e quota ---
        if not text:
            raise RuntimeError(f"LLM {provider} ha restituito testo vuoto")

        text_lower = text.lower()

        if "[errore gemini]" in text_lower or "[errore openai]" in text_lower:
            raise RuntimeError(f"LLM {provider} non disponibile o quota superata")

        return text

    except Exception as e:
        # --- Sticky fallback: attiva LLaMA per tutte le chiamate future ---
        print(f"⚠️ Fallback attivato definitivamente per {provider}: {e}")
        _FALLBACK_ACTIVE = True
        llama_resp = get_llm("llama")(prompt, **kwargs)
        return llama_resp["choices"][0]["text"].strip()

#Reset della variabile locale
def reset_fallback():
    global _FALLBACK_ACTIVE
    _FALLBACK_ACTIVE = False


# ================================================================
# FUNZIONE HELPER DIRETTA
# ================================================================
def ask(provider: str, prompt: str, **kwargs) -> str:
    return safe_llm_call(provider, prompt, **kwargs)


# ================================================================
# MODELLI E TOOL NLP
# ================================================================

MODEL_PATH = "models/model.pkl"

# Check if NLTK punkt tokenizer is available, if not download it
try:
    print("Looking for NLTK punkt tokenizer...")
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=True)

# Load the models
ft_model = fasttext.load_model("models/fasttext_model.bin")

# Load the dialog tagger
dialog_tagger = DialogTag('bert-base-uncased')

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# ================================================================
# PREPROCESSING
# ================================================================

def preprocessing(path):
    def read_txt(path):
        # Read the file
        with open(path, "r+") as conversation:
            conversation = conversation.readlines()
            ## Initial pre-processing
            # Remove empty entries
            conversation = [entry for entry in conversation if entry != '\n']
            return conversation

    def read_csv(path):
        raise NotImplementedError("CSV file reading not implemented yet")

    def read_xlsx(path):
        raise NotImplementedError("XLSX file reading not implemented yet")

    if path.endswith(".txt"):
        conversation = read_txt(path)
    elif path.endswith(".xlsx"):
        conversation = read_xlsx(path)
    elif path.endswith(".csv"):
        conversation = read_csv(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

    # Create speakerturns
    pattern = r"(?P<end_time>\[\d+\:\d+\:\d+\]) (?P<speaker>\w+)\: (?P<content>.+)"
    speakerturns = [re.match(pattern, entry) for entry in conversation]

    # Remove all empty speakerturns
    speakerturns = [turn for turn in speakerturns if turn != None]

    # Change format so each speakerturn has a unique identifier
    for i in range(0, len(speakerturns)):
        current = speakerturns[i]
        speakerturns[i] = (i, current.group('end_time'), current.group('speaker'), current.group('content'))

    df = pd.DataFrame(speakerturns,
                      columns=['identifier', 'time', 'speaker', 'text']
                      ).set_index('identifier', drop=False)
    return df

# ================================================================
# QUESTIONS IDENTIFICATION
# ================================================================

def questions_identification(conversation):
    # Whenever a dialogue acts contains "-Question" or is an "Or-Clause", we consider it to be a question.
    dialog_acts = ["-Question", "Or-Clause"]

    def is_question(s) :
        from nltk.tokenize import PunktSentenceTokenizer
        tokenizer = PunktSentenceTokenizer()

        q = False
        for sentence in tokenizer.tokenize(s) :
            tag = dialog_tagger.predict_tag(sentence)
            if any(dialog_act in tag for dialog_act in dialog_acts) :
                q = True
        return q

    processed_text = [ft_model.get_sentence_vector(sentence) for sentence in conversation['text']]

    pred = model.predict(processed_text)

    output = []
    for i in range(len(pred)) :
        if len(conversation.loc[i]['text'].split()) >= 7 :
            output.append({"text" : conversation.loc[i]['text'], "pred" : ("Req" if pred[i] == 0 else "NonReq")})

    final_predicted_rqs = []
    for i in range(len(output)) :
        if (output[i]["pred"] == "Req") :
            if (is_question(output[i]['text'])) :
                final_predicted_rqs.append(output[i]["text"] + "? " + output[i + 1]["text"])
            else :
                final_predicted_rqs.append(output[i]["text"])

    return final_predicted_rqs

# ================================================================
# REQUIREMENTS EXTRACTION
# ================================================================

def requirements_extraction(final_predicted_rqs, provider):
    llm = get_llm(provider)
    prompts = []
    for sentence in final_predicted_rqs:
        prompts.append({
            "prompt": (
                f"""
You are a senior system analyst specialized in requirements engineering.

TASK:
From the given conversation excerpt, extract ONLY explicit and clearly implied SYSTEM REQUIREMENTS, if any.

STRICT RULES:
- Extract only real system requirements, not opinions, not explanations, not context.
- A requirement must describe a capability, constraint, or behavior of the system.
- Do NOT invent, assume, or infer requirements that are not clearly supported by the text.
- If no requirements are present, output exactly: None
- Do NOT explain your reasoning.
- Do NOT rewrite the sentence.
- Do NOT add any text before or after the result.
- Each requirement must be atomic and represent a single capability or constraint.
- Do not merge multiple requirements into one.
- Do not repeat similar requirements.
- If the output format is violated, regenerate internally and correct it before responding.

OUTPUT FORMAT:
- Return ONLY a semicolon-separated list of requirements.
- Each requirement must start with: "The system must ..."
- No numbering.
- No bullet points.
- No extra spaces.
- End each requirement with a semicolon.
- If none exist, output exactly: None

EXAMPLES:

Example 1:
Excerpt: "The application should allow users to reset their password via email and must store encrypted credentials."
Output:
The system must allow users to reset their password via email;The system must store encrypted credentials;

Example 2:
Excerpt: "I think the interface looks nice but maybe it could be faster."
Output:
None

--- INPUT ---
Excerpt: "{sentence}"
--- OUTPUT ---
"""
            ),
            "sentence": sentence
        })

    output = []
    for prompt in prompts:
        try:
            result_text = safe_llm_call(
                provider,
                prompt["prompt"],
                max_tokens=512,
                temperature=0.2,
                stop=["</s>"]
            ).strip()

            print("▶︎ Prompt:", prompt["prompt"])
            print("▶︎ Response text:", result_text)

            output.append({
                "sentence": prompt["sentence"],
                "result": result_text
            })

        except Exception as e:
            print(f"Errore con LLM: {e}")
            output.append({
                "sentence": prompt["sentence"],
                "result": ""
            })

    # Parsing output per trovare le frasi con "The system must"
    final_requirements_mapping = []
    for row in output:
        results = row["result"]
        splitted = results.split("\n")
        requirements = []
        for line in splitted:
            if "The system must" in line:
                requirements.append(line.strip())
        final_requirements_mapping.append({
            "sentence": row["sentence"],
            "requirements": requirements
        })
    return final_requirements_mapping


# ================================================================
# PIPELINE
# ================================================================

def pipeline(path, provider):
    reset_fallback()
    conversation = preprocessing(path)
    predicted_requirements_phrases = questions_identification(conversation)
    return requirements_extraction(predicted_requirements_phrases, provider)

# ================================================================
# PARSING REQUIREMENTS DA FILE TXT
# ================================================================
import re
from pathlib import Path          # assicurati che l'import sia presente

#   - inizio riga, spazi opzionali
#   - trattino
#   - spazi
#   - numero + punto (facoltativo)   es. “1.”
#   - spazi
#   - requisito (catturato nel gruppo 1)
REQ_LINE = re.compile(r"^\s*-\s+(.*?);?\s*$")

def parse_requirements_txt(path: str) -> list[str]:
    requirements: list[str] = []

    with Path(path).open(encoding="utf-8") as f:
        for raw in f:
            match = REQ_LINE.match(raw.rstrip())
            if match:
                req_text = match.group(1).strip()
                if req_text:
                    split_reqs = [r.strip() for r in req_text.split(';') if r.strip()]
                    requirements.extend(split_reqs)

    return requirements


# ================================================================
# GENERAZIONE USER STORIES
# ================================================================
def generate_userstories(requirements_file_path: str, provider) -> list[dict]:
    reset_fallback()

    print("Parsing requirements file...")
    reqs = parse_requirements_txt(requirements_file_path)
    out = []

    prompt_tpl = (
        "You are a senior Business Analyst specialized in Agile requirements engineering.\n\n"
        "TASK:\n"
        "Convert the given SYSTEM REQUIREMENT into EXACTLY ONE Agile User Story.\n\n"
        "STRICT RULES:\n"
        "- Produce exactly ONE user story.\n"
        "- Follow STRICTLY the format: As a <type of user>, I want <goal> so that <reason>.\n"
        "- Do NOT add explanations, comments, titles, or extra text.\n"
        "- Do NOT generate more than one sentence.\n"
        "- Do NOT invent features, users, or motivations not supported by the requirement.\n"
        "- Keep the meaning fully consistent with the requirement.\n"
        "- If the requirement is unclear or not convertible into a user story, output exactly: None.\n"
        "- If the format is violated, regenerate internally and correct it before responding.\n\n"
        "FORMAT CONSTRAINTS:\n"
        "- Must start exactly with: \"As a \"\n"
        "- Must contain exactly one \"I want\"\n"
        "- Must contain exactly one \"so that\"\n"
        "- Must end with a period.\n"
        "- No bullet points.\n"
        "- No numbering.\n"
        "- No extra whitespace.\n\n"
        "EXAMPLES:\n\n"
        "Requirement: \"The system must allow users to reset their password via email.\"\n"
        "User story:\n"
        "As a registered user, I want to reset my password via email so that I can regain access to my account.\n\n"
        "Requirement: \"The system must log all authentication attempts.\"\n"
        "User story:\n"
        "As a system administrator, I want the system to log all authentication attempts so that I can monitor security events.\n\n"
        "Requirement: \"The interface should be visually appealing.\"\n"
        "User story:\n"
        "None\n\n"
        "--- INPUT ---\n"
        "Requirement: \"{req}\"\n"
        "--- OUTPUT ---\n"
        "User story:"
    )

    for req in reqs:
        try:
            story = safe_llm_call(provider, prompt_tpl.format(req=req), max_tokens=128, temperature=0.2, stop=["</s>"])
        except Exception as e:
            print("LLM error:", e)
            story = ""

        out.append({"requirement": req, "userstory": story})

    return out
