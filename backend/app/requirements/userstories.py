from typing import List, Dict
from app.requirements.parser import parse_requirements_txt
from app.llm.safe_call import ask, reset_fallback

def generate_userstories(requirements_file_path: str, provider: str) -> List[Dict[str, str]]:
    """
    Genera user stories a partire da un file txt contenente requisiti.

    Ogni requisito diventa ESATTAMENTE una user story secondo le regole Agile.
    """

    reset_fallback()  # resetta fallback LLaMA all’inizio

    print("Parsing requirements file...")
    reqs = parse_requirements_txt(requirements_file_path)
    out = []

    for req in reqs:
        prompt = f"""
You are a senior Business Analyst specialized in Agile requirements engineering.

TASK:
Convert the given SYSTEM REQUIREMENT into EXACTLY ONE Agile User Story.

STRICT RULES:
- Produce exactly ONE user story.
- Follow STRICTLY the format: As a <type of user>, I want <goal> so that <reason>.
- Do NOT add explanations, comments, titles, or extra text.
- Do NOT generate more than one sentence.
- Do NOT invent features, users, or motivations not supported by the requirement.
- Keep the meaning fully consistent with the requirement.
- If the requirement is unclear or not convertible into a user story, output exactly: None.
- If the format is violated, regenerate internally and correct it before responding.

FORMAT CONSTRAINTS:
- Must start exactly with: "As a "
- Must contain exactly one "I want"
- Must contain exactly one "so that"
- Must end with a period.
- No bullet points.
- No numbering.
- No extra whitespace.

EXAMPLES:

Requirement: "The system must allow users to reset their password via email."
User story:
As a registered user, I want to reset my password via email so that I can regain access to my account.

Requirement: "The system must log all authentication attempts."
User story:
As a system administrator, I want the system to log all authentication attempts so that I can monitor security events.

Requirement: "The interface should be visually appealing."
User story:
None

--- INPUT ---
Requirement: "{req}"
--- OUTPUT ---
User story:"""

        try:
            story = ask(provider, prompt, max_tokens=128, temperature=0.2, stop=["</s>"])
        except Exception as e:
            print("LLM error:", e)
            story = ""

        out.append({"requirement": req, "userstory": story})

    return out
