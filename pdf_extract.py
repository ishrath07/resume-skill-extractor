import pdfplumber
from pathlib import Path

def extract_text(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append((page.extract_text() or "").strip())
    text = "\n\n".join(p for p in pages if p)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(lines).strip()


if __name__ == "__main__":
    extracted = extract_text("data/sample_resume.pdf")
    print(extracted[:500])   # print first 500 characters to inspect