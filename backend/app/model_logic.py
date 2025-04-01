"""
ML logic module: load, preprocess, and run inference with your model.
"""
import re
import pickle
import fasttext
import pandas as pd
import numpy as np
import csv
from dialog_tag import DialogTag
from nltk import tokenize, Tree


import nltk
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

with open('models/model.pkl', 'rb') as f:
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

def pipeline(path):
    conversation = preprocessing(path)

    # Whenever a dialogue acts contains "-Question" or is an "Or-Clause", we consider it to be a question.
    dialog_acts = ["-Question", "Or-Clause"]

    def is_question(s):
        from nltk.tokenize import PunktSentenceTokenizer
        tokenizer = PunktSentenceTokenizer()

        q = False
        for sentence in tokenizer.tokenize(s):
            tag = dialog_tagger.predict_tag(sentence)
            if any(dialog_act in tag for dialog_act in dialog_acts):
                q = True
        return q


    processed_text = [ft_model.get_sentence_vector(sentence) for sentence in conversation['text']]

    pred = model.predict(processed_text)

    output = []
    for i in range(len(pred)):
        if len(conversation.loc[i]['text'].split()) >= 7:
            output.append({"text": conversation.loc[i]['text'], "pred": ("Req" if pred[i] == 0 else "NonReq")})

    final_predicted_rqs = []
    for i in range(len(output)):
        if (output[i]["pred"] == "Req"):
            if (is_question(output[i]['text'])):
                final_predicted_rqs.append(output[i]["text"] + "? " + output[i + 1]["text"])
            else:
                final_predicted_rqs.append(output[i]["text"])

    return final_predicted_rqs