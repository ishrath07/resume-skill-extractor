import html


LABEL_STYLES = {
    "SKILL": {"color": "#10b981", "bg": "rgba(16, 185, 129, 0.15)"},       # green
    "TOOL": {"color": "#3b82f6", "bg": "rgba(59, 130, 246, 0.15)"},        # blue
    "EXPERIENCE": {"color": "#f59e0b", "bg": "rgba(245, 158, 11, 0.15)"},  # amber
    "JOB_TITLE": {"color": "#a855f7", "bg": "rgba(168, 85, 247, 0.15)"},   # purple, bonus
}


def highlight_text(text, entities):
    """
    Wraps each entity span in a colored <mark> tag based on its label.
    Entities that overlap or aren't in LABEL_STYLES are skipped safely.
    """
    # Only keep entities we know how to color, and sort by start position
    relevant = [e for e in entities if e["label"] in LABEL_STYLES]
    relevant.sort(key=lambda e: e["start"])

    pieces = []
    cursor = 0

    for entity in relevant:
        start, end = entity["start"], entity["end"]

        # Skip overlapping entities (keep it simple and safe)
        if start < cursor:
            continue

        # Add the plain text before this entity
        pieces.append(html.escape(text[cursor:start]))

        # Add the highlighted entity itself
        style = LABEL_STYLES[entity["label"]]
        entity_text = html.escape(text[start:end])
        pieces.append(
            f'<mark class="ent" '
            f'style="background:{style["bg"]}; color:{style["color"]}; '
            f'border: 1px solid {style["color"]}44; '
            f'padding: 1px 6px; border-radius: 6px; font-weight: 600;" '
            f'title="{entity["label"]}">{entity_text}</mark>'
        )

        cursor = end

    # Add whatever text is left after the last entity
    pieces.append(html.escape(text[cursor:]))

    body = "".join(pieces).replace("\n", "<br>")

    return f'<div style="line-height: 1.9; font-size: 15px; white-space: normal;">{body}</div>'


if __name__ == "__main__":
    sample_text = "Worked as Software Engineer with 3 years of experience in Python and Git."
    sample_entities = [
        {"text": "Python", "label": "SKILL", "start": 47, "end": 53},
        {"text": "Git", "label": "TOOL", "start": 58, "end": 61},
        {"text": "3 years", "label": "EXPERIENCE", "start": 24, "end": 31},
    ]
    print(highlight_text(sample_text, sample_entities))