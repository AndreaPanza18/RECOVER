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
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

ft_model = fasttext.load_model("models/fasttext_model.bin")
with open('models/model.pkl', 'rb') as f:
    model = pickle.load(f)

def pipeline(path):
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

    conversation = preprocessing(path)
    # Speech Act Classification Model
    dialog_tagger = DialogTag('bert-base-uncased')

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


def load_model():
    """
    Load or initialize the machine learning model.
    Returns:
        model (any): An instance of your model, e.g. a scikit-learn or PyTorch object.
    """
    # TODO: Replace with actual loading logic
    # Example:
    # model = joblib.load("path_to_saved_model.joblib")
    # return model
    return "fake_model"

def run_inference(model, data):
    """
    Run inference on the given data using the provided model.
    Args:
        model (any): The ML model instance.
        data (str or other): Input data to be processed by the model.
    Returns:
        result (any): The model's output or prediction.
    """
    # TODO: Replace with your real inference logic
    # Example:
    # return model.predict([data])[0]
    return f"Inference result for input: '{data}'"
