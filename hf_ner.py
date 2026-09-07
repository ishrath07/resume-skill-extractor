from src.ner import extract_entities

try:
    from transformers import pipeline
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

_hf_pipeline = None  # cache so we don't reload the model every call


def _get_pipeline():
    global _hf_pipeline
    if _hf_pipeline is None:
        _hf_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple",
        )
    return _hf_pipeline


def _chunk_text(text, max_chars=800):
    """Split text into chunks so we stay under BERT's token limit, keeping offsets correct."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        # try to break on a newline so we don't cut a word in half
        if end < len(text):
            newline_pos = text.rfind("\n", start, end)
            if newline_pos > start:
                end = newline_pos
        chunks.append((start, text[start:end]))
        start = end
    return chunks


def get_hf_entities(text):
    """
    Runs dslim/bert-base-NER over the (possibly long) text in chunks,
    and returns entities in {text, label, start, end} shape with
    correct offsets relative to the ORIGINAL full text.
    """
    ner_pipeline = _get_pipeline()
    entities = []

    for chunk_start, chunk_text in _chunk_text(text):
        if not chunk_text.strip():
            continue
        raw_results = ner_pipeline(chunk_text)
        for r in raw_results:
            entities.append({
                "text": r["word"],
                "label": r["entity_group"],
                "start": chunk_start + r["start"],
                "end": chunk_start + r["end"],
            })

    return entities


def compare(text):
    print(f"Sentence: {text}\n")

    print("--- Your spaCy + ruler entities ---")
    spacy_results = extract_entities(text)
    if not spacy_results:
        print("(none found)")
    for e in spacy_results:
        print(f"  {e['label']:<12} {e['text']}")

    print("\n--- Hugging Face (dslim/bert-base-NER) entities ---")
    if not HF_AVAILABLE:
        print("(torch/transformers not installed — skipping. You still learned the idea!)")
        return

    try:
        hf_results = get_hf_entities(text)
        if not hf_results:
            print("(none found)")
        for e in hf_results:
            print(f"  {e['label']:<12} {e['text']}")
    except Exception as ex:
        print(f"(Hugging Face model failed to load or run: {ex})")
        print("You still learned the idea!")


if __name__ == "__main__":
    sample = "Jane Doe worked at Microsoft in Seattle using Python."
    compare(sample)