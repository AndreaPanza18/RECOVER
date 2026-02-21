import re
import pandas as pd
from pathlib import Path

def preprocessing(path: str) -> pd.DataFrame:

    def read_txt(path: str):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Rimuove righe vuote
        lines = [line for line in lines if line.strip()]
        return lines

    def read_csv(path: str):
        raise NotImplementedError("Lettura CSV non implementata ancora")

    def read_xlsx(path: str):
        raise NotImplementedError("Lettura XLSX non implementata ancora")

    path_obj = Path(path)
    if path_obj.suffix.lower() == ".txt":
        conversation = read_txt(path)
    elif path_obj.suffix.lower() == ".csv":
        conversation = read_csv(path)
    elif path_obj.suffix.lower() == ".xlsx":
        conversation = read_xlsx(path)
    else:
        raise ValueError(f"Tipo file non supportato: {path}")

    pattern = r"(?P<end_time>\[\d+:\d+:\d+\]) (?P<speaker>\w+)\: (?P<content>.+)"
    speakerturns = [re.match(pattern, line) for line in conversation]
    speakerturns = [turn for turn in speakerturns if turn is not None]

    # Assegna identificatore unico
    for i, turn in enumerate(speakerturns):
        speakerturns[i] = (i, turn.group('end_time'), turn.group('speaker'), turn.group('content'))

    df = pd.DataFrame(
        speakerturns,
        columns=['identifier', 'time', 'speaker', 'text']
    ).set_index('identifier', drop=False)

    return df
