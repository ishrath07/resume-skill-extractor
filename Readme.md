# Resume Skill Extractor

## 1. The Recruiter Problem

Recruiters often have to read many resumes and manually look for relevant skills, tools, and experience. This project makes that process faster by allowing a recruiter to upload a resume PDF and automatically highlight the important information. The app also shows the extracted sections and the results in JSON format.

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

## 3. The Labels Used

The custom extractor uses three main labels:

* **SKILL** — programming languages, frameworks, or technical skills
* **TOOL** — software, platforms, or development tools
* **EXPERIENCE** — experience-related information

These labels are also displayed in the application's highlight legend.

## 4. Limitations

The extractor depends on the skills and tools included in its vocabulary, so **unknown skills can be missed until they are added**. PDF text extraction can also be imperfect, especially when a resume uses columns or complex layouts, because the extracted text may not preserve the original reading order.

The Hugging Face model shown in the comparison is **not a resume-skill model**. It uses generic entity categories rather than being specifically trained for the project's SKILL/TOOL vocabulary, so its results should not be treated as a direct replacement for the custom extractor.
