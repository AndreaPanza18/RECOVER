from app.nlp.models_loader import ft_model, dialog_tagger, model

def questions_identification(conversation):

    # Dialog acts considerati question
    dialog_acts = ["-Question", "Or-Clause"]

    def is_question(s: str) -> bool:
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
            output.append({
                "text": conversation.loc[i]['text'],
                "pred": "Req" if pred[i] == 0 else "NonReq"
            })

    final_predicted_rqs = []
    for i in range(len(output)):
        if output[i]["pred"] == "Req":
            if is_question(output[i]['text']):
                if i + 1 < len(output):
                    final_predicted_rqs.append(output[i]["text"] + "? " + output[i + 1]["text"])
                else:
                    final_predicted_rqs.append(output[i]["text"])
            else:
                final_predicted_rqs.append(output[i]["text"])

    return final_predicted_rqs
