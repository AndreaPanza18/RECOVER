from app.nlp.preprocessing import preprocessing
from app.nlp.question_detection import questions_identification
from app.requirements.extractor import requirements_extraction
from app.llm.safe_call import reset_fallback
from app.requirements.classifier import classify_requirements

def pipeline(file_path: str, provider: str):

    # Preprocessing
    sentences = preprocessing(file_path)

    # Question detection
    detected = questions_identification(sentences)

    # Requirement extraction
    extracted = requirements_extraction(detected, provider)

    # Classification
    functional, non_functional = classify_requirements(extracted, provider)

    return {
        "functional": functional,
        "non_functional": non_functional
    }

