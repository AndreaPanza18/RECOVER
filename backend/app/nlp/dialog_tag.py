class DialogTag:

    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model_name = model_name

    def predict_tag(self, text: str) -> str:
        """
        Restituisce una stringa di tag di esempio per la frase.
        Sostituire con logica reale di dialog tagging.
        """

        if "?" in text:
            return "-Question"
        return "Statement"
