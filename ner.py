import spacy
from spacy.matcher import Matcher
from pathlib import Path


def load_lines(path):
    """Read a text file and return a list of non-empty lines."""
    return [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_nlp():
    nlp = spacy.load("en_core_web_sm")

    # --- EntityRuler: your own skill/tool word lists ---
    ruler = nlp.add_pipe(
        "entity_ruler",
        before="ner",
        config={"phrase_matcher_attr": "LOWER"},
    )

    skills = load_lines("data/skills.txt")
    tools = load_lines("data/tools.txt")

    # Longer phrases first, so "machine learning" wins over just "learning"
    skills.sort(key=len, reverse=True)
    tools.sort(key=len, reverse=True)

    patterns = [{"label": "SKILL", "pattern": s} for s in skills]
    patterns += [{"label": "TOOL", "pattern": t} for t in tools]
    ruler.add_patterns(patterns)

    return nlp


def build_matcher(nlp):
    matcher = Matcher(nlp.vocab)

    # Pattern for something like "3 years"
    matcher.add("EXPERIENCE_YEARS", [[
        {"LIKE_NUM": True},
        {"LOWER": "years"},
    ]])

    # Pattern for job titles like "software engineer"
    matcher.add("JOB_TITLE", [[
        {"LOWER": "software"},
        {"LOWER": "engineer"},
    ]])

    return matcher


nlp = build_nlp()
matcher = build_matcher(nlp)


def extract_entities(text):
    doc = nlp(text)
    results = []

    # From EntityRuler + spaCy's own default ner
    for ent in doc.ents:
        if ent.label_ in ("SKILL", "TOOL"):
            source = "ruler"
        else:
            source = "spacy_ner"
        results.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
            "source": source,
        })

    # From the Matcher (years, job titles)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        label = nlp.vocab.strings[match_id]  # "EXPERIENCE_YEARS" or "JOB_TITLE"
        results.append({
            "text": span.text,
            "label": "EXPERIENCE" if label == "EXPERIENCE_YEARS" else "JOB_TITLE",
            "start": span.start_char,
            "end": span.end_char,
            "source": "matcher",
        })

    return results


if __name__ == "__main__":
    sample = "Worked as Software Engineer with 3 years of experience in Python and Git"
    for entity in extract_entities(sample):
        print(entity)