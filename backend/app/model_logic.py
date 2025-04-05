"""
ML logic module: load, preprocess, and run inference with your model.
"""
import re
import pickle
import fasttext
import pandas as pd
import numpy as np
import csv
import nltk
from dialog_tag import DialogTag
from nltk import tokenize, Tree
from llama_cpp import Llama

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        print("⚡ Loading LLaMA model for the first time...")
        _llm = Llama(
            model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
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

def requirements_extraction(final_predicted_rqs):
    llm = get_llm()
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
                "Example output: '1. The system must have example feature X; 2. The system must have example feature Y;' "
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

def pipeline(path):
    conversation = preprocessing(path)
    predicted_requirements_phrases = questions_identification(conversation)
    return requirements_extraction(predicted_requirements_phrases)

