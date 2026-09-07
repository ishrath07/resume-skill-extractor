def to_json(entities):
    """
    Groups a list of entity dictionaries by their 'label'.

    Each entity dict looks like:
        {"text": "Python", "label": "SKILL", "start": 6, "end": 12}

    Returns something like:
        {"SKILL": ["Python"], "TOOL": ["Git"]}
    """
    grouped = {}

    for entity in entities:
        label = entity["label"]
        text = entity["text"]

        if label not in grouped:
            grouped[label] = []

        grouped[label].append(text)

    return grouped
def build_result(text, sections, entities):
    # Attach each entity to the section it falls inside
    enriched_entities = []
    for entity in entities:
        entity_section = None
        for section in sections:
            if section["start"] <= entity["start"] < section["end"]:
                entity_section = section["name"]
                break

        enriched_entities.append({
            "text": entity["text"],
            "label": entity["label"],
            "start": entity["start"],
            "end": entity["end"],
            "section": entity_section,
        })

    # Group SKILL, TOOL, EXPERIENCE into by_label, skipping duplicates
    by_label = {}
    for entity in enriched_entities:
        label = entity["label"]
        if label not in ("SKILL", "TOOL", "EXPERIENCE"):
            continue
        if label not in by_label:
            by_label[label] = []
        if entity["text"] not in by_label[label]:
            by_label[label].append(entity["text"])

    return {
        "char_count": len(text),
        "sections": sections,
        "entities": enriched_entities,
        "by_label": by_label,
    }


if __name__ == "__main__":
    sample_text = "I use Python and Git."
    sample_entities = [
        {"text": "Python", "label": "SKILL", "start": 6, "end": 12},
        {"text": "Git", "label": "TOOL", "start": 17, "end": 20},
    ]

    print(sample_text[6:12])   # should print Python
    print(sample_text[17:20])  # should print Git

    print(to_json(sample_entities))