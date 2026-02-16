from typing import List, Dict
from app.llm.safe_call import ask

def requirements_extraction(final_predicted_rqs: List[str], provider: str) -> List[Dict[str, any]]:

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
- If none exist, output exactly: None
- No numbering, no bullets, no extra spaces, end each requirement with a semicolon.
- Do NOT leave it empty, ALWAYS return something (at least 'None').

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
            result_text = ask(
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
                "result": "None"
            })

    final_requirements_mapping = []

    for row in output:
        results = row["result"]
        splitted = results.split("\n")
        requirements = []

        for line in splitted:
            line = line.strip()
            if line.startswith("The system must") and len(line.replace("The system must", "").strip(" :;")) > 0:
                requirements.append(line)

        if requirements:
            final_requirements_mapping.append({
                "sentence": row["sentence"],
                "requirements": requirements
            })

    return final_requirements_mapping
