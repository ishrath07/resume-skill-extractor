# Resume Skill Extractor

## 1. The Recruiter Problem

Recruiters often have to read many resumes and manually look for relevant skills, tools, and experience — and then, for a specific opening, figure out how well each resume actually fits the job description. This project speeds up both steps: a recruiter (or a job seeker) can upload a resume PDF to automatically extract and highlight the important information, and can also paste a job description to get a match score against that resume, along with concrete suggestions on what to add.

## 2. How to Install and Run

Clone or download the project and install the required Python packages:

```bash
pip install -r requirements.txt
```

The project uses libraries such as `pdfplumber`, `spaCy`, `Gradio`, and `reportlab`.

Then run the application:

```bash
python app.py
```

Open the Gradio link shown in the terminal, upload a resume PDF, and click **Extract**. The application will display the highlighted resume, detected sections, JSON output, evaluation results, and a spaCy vs. Hugging Face comparison.

To check how well the resume fits a specific role, go to the **JD Match** tab, paste in the job description, and click **Match**. This shows a match score, the keywords the resume already covers, the keywords it's missing, and suggestions for tailoring the resume to that job description.

## 3. The Labels Used

The custom extractor uses three main labels:

* **SKILL** — programming languages, frameworks, or technical skills
* **TOOL** — software, platforms, or development tools
* **EXPERIENCE** — experience-related information

These labels are also displayed in the application's highlight legend.

## 4. JD Match — Resume-to-Job-Description Matching

The **JD Match** tab lets you paste a job description and see how well the uploaded resume aligns with it.

* The same `SKILL`/`TOOL` extractor used on resumes is run on the job description text, so both are compared using the same vocabulary.
* **Match score** — the percentage of the job description's required skills/tools that are also found on the resume.
* **Matched keywords** — skills/tools that appear in both the resume and the JD.
* **Missing keywords** — skills/tools the JD asks for that weren't found on the resume, ranked by how often the JD mentions them (more mentions = higher priority to consider adding).
* **Extra keywords** — skills/tools on the resume that the JD didn't ask for (shown for context, not necessarily a problem).
* **Suggestions** — plain-English guidance based on the overall match level and the specific gaps found.

This feature reuses the resume's already-extracted entities rather than re-running extraction, so matching against a new job description is quick even for the same uploaded resume.

## 5. Limitations

The extractor depends on the skills and tools included in its vocabulary, so **unknown skills can be missed until they are added**. PDF text extraction can also be imperfect, especially when a resume uses columns or complex layouts, because the extracted text may not preserve the original reading order.

The Hugging Face model shown in the comparison is **not a resume-skill model**. It uses generic entity categories rather than being specifically trained for the project's SKILL/TOOL vocabulary, so its results should not be treated as a direct replacement for the custom extractor.

The JD Match feature is **keyword-based, not semantic** — it relies on the same fixed vocabulary as the resume extractor. If a job description or resume uses phrasing that isn't in `skills.txt`/`tools.txt` (e.g. "ML" instead of "Machine Learning"), it won't be recognized as a match even if the underlying skill is the same. The match score should be treated as a directional signal, not a definitive assessment of fit.
