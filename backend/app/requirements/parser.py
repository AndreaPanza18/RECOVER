import re
from pathlib import Path
from typing import List

REQ_LINE = re.compile(r"^\s*-\s+(.*?);?\s*$")


def parse_requirements_txt(path: str) -> List[str]:
    requirements: List[str] = []

    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"File requisiti non trovato: {path}")

    with path_obj.open(encoding="utf-8") as f:
        for raw in f:
            match = REQ_LINE.match(raw.rstrip())
            if match:
                req_text = match.group(1).strip()
                if req_text:
                    split_reqs = [r.strip() for r in req_text.split(';') if r.strip()]
                    requirements.extend(split_reqs)

    return requirements
