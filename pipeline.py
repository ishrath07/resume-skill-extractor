from src.ner import extract_entities
from src.pdf_extract import extract_text
from src.schema import build_result
from src.sections import detect_sections


def analyze_text(text):
    sections = detect_sections(text)
    entities = extract_entities(text)
    return build_result(text, sections, entities)


def analyze_pdf(path):
    text = extract_text(path)
    return text, analyze_text(text)