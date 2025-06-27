import pickle
import os
import fasttext
import pandas as pd
import nltk
import re
from dialog_tag import DialogTag
from llama_cpp import Llama
import google.generativeai as genai

# Carica .env solo per API_KEY e MODEL_NAME
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Globals per caching
_llm = None
_current_provider = None

# Configura le tue variabili (API_KEY, MODEL_NAME) in .env
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
def get_llm(provider: str):
    global _llm, _current_provider
    # Se cambia provider, resetta LLM
    if provider != _current_provider:
        _current_provider = provider
        _llm = None

    if _llm is None:
        if provider == "genai":
            model_name = os.getenv("GENAI_MODEL", "models/gemini-1.5-flash-latest")
            model = genai.GenerativeModel(model_name)
            def genai_llm(prompt, **kwargs):
                resp = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": kwargs.get("temperature", 0.2),
                        "max_output_tokens": kwargs.get("max_tokens", 512)
                    }
                )
                return {"choices": [{"text": resp.text.strip()}]}
            _llm = genai_llm
        else:
            model_path = os.path.join(
                "models",
                os.getenv("LLM_MODEL_FILE", "llama-2-7b-chat.Q4_K_M.gguf")
            )
            _llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=4
            )
    return _llm



#Constants
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

def requirements_extraction(final_predicted_rqs, provider):
    llm = get_llm(provider)
    prompts = []
    for sentence in final_predicted_rqs:
        prompts.append({
            "prompt": (
                "Given the following excerpt of a conversation, derive the system requirements: '"
                + sentence +
                "', if any. Please answer only with the list of derived requirements as output as shown in the following examples. "
                "Please do not consider the example excerpts provided in the examples in your final answer. "
                "---- Example 1: ---- "
                "Example excerpt: 'Excerpt of conversation containing system requirements' "
                "Example output: 'The system must have example feature X;The system must have example feature Y;' "
                "---- Example 2: ---- "
                "Example excerpt: 'Excerpt of conversation that does not contain system requirements' "
                "Example output: 'None'"
            ),
            "sentence": sentence
        })

    output = []
    for prompt in prompts:
        try:
            response = llm(
                prompt["prompt"],
                max_tokens=512,
                temperature=0.2,
                stop=["</s>"]
            )
            result_text = response["choices"][0]["text"].strip()
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

def pipeline(path, provider):
    conversation = preprocessing(path)
    predicted_requirements_phrases = questions_identification(conversation)
    return requirements_extraction(predicted_requirements_phrases, provider)

# ---------------------------------------------------------------
# 1.1  Parser del file .txt “Frase origine …   - 1. requisito …”
# ---------------------------------------------------------------
import re
from pathlib import Path          # assicurati che l'import sia presente

#   - inizio riga, spazi opzionali
#   - trattino
#   - spazi
#   - numero + punto (facoltativo)   es. “1.”
#   - spazi
#   - requisito (catturato nel gruppo 1)
REQ_LINE = re.compile(r"^\s*-\s*(?:\d+\.\s*)?(.*)$")

def parse_requirements_txt(path: str) -> list[str]:
    """
    Estrae SOLO i requisiti dalle righe con bullet (- 1. …).
    Ignora “Frase origine:” e righe vuote.
    """
    requirements: list[str] = []

    # puoi usare anche open(path, ... ) se preferisci
    with Path(path).open(encoding="utf-8") as f:
        for raw in f:
            match = REQ_LINE.match(raw.rstrip())
            if match:
                req_text = match.group(1).strip()
                if req_text:                 # scarta righe vuote
                    requirements.append(req_text)

    return requirements



# ---------------------------------------------------------------
# 1.2  Generazione user story via LLM (output = pipeline-style)
# ---------------------------------------------------------------
def generate_userstories(requirements_file_path: str, provider) -> list[dict]:
    """
    :returns:
      [
        { "requirement": "<req>", "userstory": "<story>" },
        ...
      ]
    """
    llm   = get_llm(provider)
    reqs  = parse_requirements_txt(requirements_file_path)
    out   = []

    prompt_tpl = (
        "You are an expert Business Analyst. Convert the following **system "
        "requirement** into ONE agile user story in the format:\n"
        "As a <type of user>, I want <some goal> so that <some reason>.\n\n"
        "Requirement: \"{req}\"\n\n"
        "User story:"
    )

    for req in reqs:
        try:
            res = llm(
                prompt_tpl.format(req=req),
                max_tokens=128,
                temperature=0.2,
                stop=["</s>"]
            )
            story = res["choices"][0]["text"].strip()
        except Exception as e:
            print("LLM error:", e)
            story = ""

        out.append({"requirement": req, "userstory": story})

    return out
