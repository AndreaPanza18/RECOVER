from app.llm.safe_call import ask

def classify(requirement: str, provider: str) -> str:
    prompt = f"""
You are an expert in software requirements engineering.
Classify the following requirement as either FUNC or NONFUNC.
Respond ONLY with FUNC or NONFUNC, nothing else.

If the requirement describes WHAT the system does → FUNC.
If it describes HOW WELL / constraints / qualities → NONFUNC.
Performance, security, reliability, scalability → NONFUNC.

Examples:

Requirement: "The system must allow users to reset their password."
Response: FUNC

Requirement: "The system must store transaction history."
Response: FUNC

Requirement: "The system must respond within 2 seconds."
Response: NONFUNC

Requirement: "The system must encrypt user data."
Response: NONFUNC

Requirement: "The system must support 10,000 concurrent users."
Response: NONFUNC

Requirement:
"{requirement}"
Response:
"""
    response = ask(
        provider,
        prompt,
        max_tokens=10,
        temperature=0.0,
        stop=["\n"]
    )

    print("\n[CLASSIFIER]")
    print("REQ:", requirement)
    print("RAW:", response)

    if not response:
        print("→ FUNC (fallback)")
        return "FUNC"

    response = response.strip().upper()
    if response not in ("FUNC", "NONFUNC"):
        print("→ FUNC (fallback non chiaro)")
        return "FUNC"

    print(f"→ {response}")
    return response


def classify_requirements(results, provider):
    functional = []
    non_functional = []

    for item in results:
        sentence = item["sentence"]
        reqs = item.get("requirements", [])

        func_reqs = []
        nonfunc_reqs = []

        for r in reqs:
            label = classify(r, provider)
            if label == "FUNC":
                func_reqs.append(r)
            else:
                nonfunc_reqs.append(r)

        if func_reqs:
            functional.append({
                "sentence": sentence,
                "requirements": func_reqs
            })

        if nonfunc_reqs:
            non_functional.append({
                "sentence": sentence,
                "requirements": nonfunc_reqs
            })

    return functional, non_functional
