import re


# Maps many possible headings to one standard name
SECTION_ALIASES = {
    "SUMMARY": ["summary", "professional summary", "career summary"],
    "SKILLS": ["skills", "technical skills", "core skills"],
    "EXPERIENCE": ["experience", "work experience", "professional experience"],
    "PROJECTS": ["projects", "personal projects"],
    "CERTIFICATIONS": ["certifications & achievements", "certifications", "achievements"],
    "EDUCATION": ["education", "academic background"],
}

# A piece of text counts as "contact info" if it has an email, a link, or a phone number
CONTACT_PATTERN = re.compile(
    r"(@|https?://|www\.|linkedin\.com|github\.com|\.vercel\.app|\.com|\+\d{1,3}[\s-]?\d)",
    re.IGNORECASE,
)


def normalize_heading(line):
    """Return the standard section name for a heading line, or None."""
    cleaned = line.strip().lower().rstrip(":")
    for standard_name, variants in SECTION_ALIASES.items():
        if cleaned in variants:
            return standard_name
    return None


def is_contact_piece(piece):
    return bool(CONTACT_PATTERN.search(piece))


def split_top_block(text):
    """
    Splits the text above the first heading into HEADLINE (name, tagline,
    location) and CONTACT (phone, email, links) — even when they're mixed
    together on the same line, separated by '|'.
    """
    blocks = []
    current_name = None
    current_parts = []
    current_start = None
    last_end = 0

    cursor = 0
    for line in text.splitlines():
        line_start = cursor
        pos = 0

        # Split the line on '|' but keep track of where each piece sits
        for piece in re.split(r"(\|)", line):
            if piece != "|" and piece.strip():
                piece_start = line_start + pos
                piece_end = piece_start + len(piece)
                label = "CONTACT" if is_contact_piece(piece) else "HEADLINE"

                if label != current_name:
                    if current_parts:
                        blocks.append({
                            "name": current_name,
                            "text": " | ".join(p.strip() for p in current_parts),
                            "start": current_start,
                            "end": last_end,
                        })
                    current_name = label
                    current_parts = [piece]
                    current_start = piece_start
                else:
                    current_parts.append(piece)

                last_end = piece_end
            pos += len(piece)

        cursor = line_start + len(line) + 1  # +1 for the newline

    if current_parts:
        blocks.append({
            "name": current_name,
            "text": " | ".join(p.strip() for p in current_parts),
            "start": current_start,
            "end": last_end,
        })

    return blocks


def detect_sections(text):
    lines = text.splitlines()

    # First, find every heading and its position in the text
    headings = []  # list of (standard_name, start_char_of_heading, end_char_of_heading_line)
    cursor = 0
    for line in lines:
        line_start = cursor
        line_end = cursor + len(line)
        standard_name = normalize_heading(line)
        if standard_name:
            headings.append((standard_name, line_start, line_end))
        cursor = line_end + 1  # +1 for the newline character

    sections = []

    # Text before the first heading = split into HEADLINE and CONTACT
    if headings:
        first_start = headings[0][1]
        top_text = text[0:first_start]
        sections.extend(split_top_block(top_text))
    else:
        # No headings found at all — split whatever text there is
        sections.extend(split_top_block(text))
        return sections

    # Now slice text between each heading and the next
    for i, (name, h_start, h_end) in enumerate(headings):
        content_start = h_end + 1  # skip past the heading line itself
        if i + 1 < len(headings):
            content_end = headings[i + 1][1]
        else:
            content_end = len(text)

        section_text = text[content_start:content_end].strip()
        sections.append({
            "name": name,
            "text": section_text,
            "start": content_start,
            "end": content_end,
        })

    return sections


if __name__ == "__main__":
    sample_text = """ISHRATH FATHIMA
Aspiring AI/ML Engineer | GenAI & RAG | Open to Entry-Level & Internships
Bengaluru, Karnataka, India | +91 7349562966 | ishrathfathima909@gmail.com
linkedin.com/in/ishrathfathima | github.com/ishrath07 | ishrathfathima.vercel.app
PROFESSIONAL SUMMARY
Final-year AI/ML student specializing in Generative AI and RAG. Built a production-style RAG chatbot at Bosch (Azure
OpenAI GPT-4o, LangChain) that cut document review time by 70% and improved retrieval accuracy by 80%, with results
validated via precision, recall, and F1-score across the ML pipeline.
TECHNICAL SKILLS
Python, SQL, React, FastAPI, machine learning

WORK EXPERIENCE
Software Engineer with 3 years of experience in Python and Git.

EDUCATION
B.E. in Computer Science, 2021"""

    for section in detect_sections(sample_text):
        print(f"--- {section['name']} ({section['start']}:{section['end']}) ---")
        print(section["text"])
        print()