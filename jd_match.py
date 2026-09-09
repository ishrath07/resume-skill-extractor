import re
from collections import Counter

from src.ner import extract_entities


MATCH_LABELS = ("SKILL", "TOOL")


def _keyword_counts_in_text(text, keywords):
    """Counts how many times each keyword literally appears in text (case-insensitive)."""
    lowered = text.lower()
    counts = {}
    for kw in keywords:
        pattern = re.escape(kw.lower())
        counts[kw] = len(re.findall(pattern, lowered))
    return counts


def _unique_keywords(entities, labels=MATCH_LABELS):
    """
    Returns a de-duplicated, original-cased list of entity texts for the given labels.
    Case-insensitive de-dup: first-seen casing wins (e.g. "python" and "Python" -> "Python").
    """
    seen_lower = set()
    unique = []
    for e in entities:
        if e["label"] not in labels:
            continue
        key = e["text"].strip().lower()
        if key and key not in seen_lower:
            seen_lower.add(key)
            unique.append(e["text"].strip())
    return unique


def extract_jd_keywords(jd_text):
    """Runs the same SKILL/TOOL extractor used on resumes, on a job description."""
    jd_entities = extract_entities(jd_text)
    return _unique_keywords(jd_entities)


def build_suggestions(match_score, missing_keywords, jd_keyword_count):
    """Plain-English, actionable suggestions based on the score and gaps."""
    suggestions = []

    if jd_keyword_count == 0:
        suggestions.append(
            "No specific skills/tools were detected in the job description. "
            "Try pasting the full JD text (including the requirements/qualifications section)."
        )
        return suggestions

    if match_score >= 0.75:
        suggestions.append(
            "Strong match — your resume already covers most of what this JD asks for. "
            "Focus on polishing phrasing and quantifying your impact rather than adding new keywords."
        )
    elif match_score >= 0.45:
        suggestions.append(
            "Moderate match. You cover a good chunk of the JD's requirements, but there's a "
            "meaningful gap — review the missing keywords below and add the ones you genuinely have experience with."
        )
    else:
        suggestions.append(
            "Low match. Your resume currently reflects less than half of what this JD is looking for. "
            "Consider tailoring your Skills and Experience sections specifically for this role before applying."
        )

    if missing_keywords:
        top = missing_keywords[:8]
        suggestions.append(
            "Keywords this JD emphasizes that weren't found on your resume: " + ", ".join(top) +
            ". If you have real experience with any of these, add them explicitly — many recruiters and "
            "ATS systems filter by exact keyword match, not synonyms."
        )

    suggestions.append(
        "Only add keywords you can genuinely speak to in an interview — padding your resume with "
        "unfamiliar terms usually backfires."
    )

    return suggestions


def match_resume_to_jd(resume_entities, jd_text):
    """
    Compares a resume's already-extracted entities against a job description.

    resume_entities: list of entity dicts, e.g. result["entities"] from schema.build_result()
    jd_text: raw job description text (string)

    Returns a dict with match_score, matched/missing/extra keyword lists, and suggestions.
    """
    resume_keywords = _unique_keywords(resume_entities)
    jd_keywords = extract_jd_keywords(jd_text)

    resume_lower = {k.lower(): k for k in resume_keywords}
    jd_lower = {k.lower(): k for k in jd_keywords}

    matched_lower = set(jd_lower) & set(resume_lower)
    missing_lower = set(jd_lower) - set(resume_lower)
    extra_lower = set(resume_lower) - set(jd_lower)

    match_score = (len(matched_lower) / len(jd_lower)) if jd_lower else 0.0

    # Rank missing keywords by how often the JD mentions them (more mentions = higher priority)
    jd_freq = _keyword_counts_in_text(jd_text, [jd_lower[k] for k in missing_lower])
    missing_sorted = sorted(
        [jd_lower[k] for k in missing_lower],
        key=lambda kw: jd_freq.get(kw, 0),
        reverse=True,
    )

    matched_sorted = sorted(jd_lower[k] for k in matched_lower)
    extra_sorted = sorted(resume_lower[k] for k in extra_lower)

    suggestions = build_suggestions(match_score, missing_sorted, len(jd_lower))

    return {
        "match_score": round(match_score, 3),
        "matched_keywords": matched_sorted,
        "missing_keywords": missing_sorted,
        "extra_keywords": extra_sorted,
        "jd_keyword_count": len(jd_lower),
        "resume_keyword_count": len(resume_lower),
        "suggestions": suggestions,
    }


if __name__ == "__main__":
    sample_resume_entities = [
        {"text": "Python", "label": "SKILL"},
        {"text": "FastAPI", "label": "SKILL"},
        {"text": "Git", "label": "TOOL"},
    ]
    sample_jd = """
    We are looking for a backend engineer with strong Python skills.
    Experience with FastAPI, Docker, and AWS is required. Python, Python, Python.
    Familiarity with Kubernetes is a plus.
    """
    result = match_resume_to_jd(sample_resume_entities, sample_jd)
    print(result)