import time
import json
import gradio as gr

from src.pipeline import analyze_pdf
from src.highlight import highlight_text
from src.ner import extract_entities
from src.metrics import precision_recall_f1, measure_latency_ms
from src.hf_ner import get_hf_entities, HF_AVAILABLE


def load_gold(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


CUSTOM_CSS = """
.gradio-container {
    background: radial-gradient(circle at top left, #0f1c1c 0%, #0a1414 100%) !important;
    font-family: 'Inter', system-ui, sans-serif;
}
#title {
    text-align: center;
    font-size: 2.1rem;
    font-weight: 800;
    background: linear-gradient(90deg, #14b8a6, #5eead4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
#subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 1.2rem;
}
.panel {
    border-radius: 16px !important;
    border: 1px solid rgba(20, 184, 166, 0.25) !important;
    background: rgba(255,255,255,0.02) !important;
    padding: 10px !important;
}
#latency-box {
    text-align: center;
    font-size: 0.85rem;
    color: #5eead4;
    margin-top: 4px;
}
.legend-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
}

/* --- Search-bar style upload row --- */
#search-bar-row {
    max-width: 620px;
    margin: 0 auto 1.4rem auto !important;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(20, 184, 166, 0.3);
    border-radius: 999px !important;
    overflow: hidden;
    padding: 4px !important;
}
#search-bar-row .form {
    border: none !important;
    background: transparent !important;
}
#file-pill {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
#file-pill > div {
    border: none !important;
    min-height: 40px !important;
    padding: 0 12px !important;
}
#extract-pill {
    border-radius: 999px !important;
    height: 40px !important;
    min-width: 110px !important;
}

/* --- Fix: keep filename left-aligned after upload --- */
#file-pill .file-preview,
#file-pill [data-testid="file"],
#file-pill table,
#file-pill tbody,
#file-pill tr {
    justify-content: flex-start !important;
    text-align: left !important;
    display: flex !important;
}
#file-pill .file-preview td:first-child,
#file-pill .filename {
    text-align: left !important;
    margin-right: auto !important;
}
"""

LEGEND_HTML = """
<div style="margin-bottom: 10px;">
    <span class="legend-badge" style="background:rgba(16,185,129,0.15); color:#10b981; border:1px solid #10b98144;">SKILL</span>
    <span class="legend-badge" style="background:rgba(59,130,246,0.15); color:#3b82f6; border:1px solid #3b82f644;">TOOL</span>
    <span class="legend-badge" style="background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid #f59e0b44;">EXPERIENCE</span>
</div>
"""


def build_sections_html(sections):
    cards = []
    for section in sections:
        preview = section["text"][:400]
        if len(section["text"]) > 400:
            preview += "…"
        cards.append(f"""
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                        border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;">
                <div style="color:#5eead4; font-weight:700; font-size:13px; letter-spacing:0.06em;
                            text-transform:uppercase; margin-bottom:6px;">{section['name']}</div>
                <div style="color:#d1d5db; font-size:14px; line-height:1.6; white-space:pre-wrap;">{preview}</div>
            </div>
        """)
    return "".join(cards) if cards else "<p style='color:#6b7280;'>No sections detected.</p>"


def build_metrics_html(scores, latency_ms):
    def metric_card(label, value, color):
        return f"""
            <div style="flex:1; min-width:120px; background: rgba(255,255,255,0.03);
                        border: 1px solid {color}44; border-radius: 14px; padding: 16px;
                        text-align:center;">
                <div style="color:{color}; font-size:28px; font-weight:800;">{value}</div>
                <div style="color:#9ca3af; font-size:12px; text-transform:uppercase;
                            letter-spacing:0.06em; margin-top:4px;">{label}</div>
            </div>
        """

    cards = "".join([
        metric_card("Precision", f"{scores['precision']*100:.0f}%", "#10b981"),
        metric_card("Recall", f"{scores['recall']*100:.0f}%", "#3b82f6"),
        metric_card("F1 Score", f"{scores['f1']*100:.0f}%", "#f59e0b"),
        metric_card("Latency", f"{latency_ms:.1f} ms", "#a855f7"),
    ])

    detail = f"""
        <div style="margin-top:16px; color:#9ca3af; font-size:13px; text-align:center;">
            True positives: {scores['true_positives']} &nbsp;·&nbsp;
            Gold entities: {scores['gold_count']} &nbsp;·&nbsp;
            Predicted entities: {scores['predicted_count']}
        </div>
    """

    return f"""
        <div style="display:flex; gap:12px; flex-wrap:wrap;">{cards}</div>
        {detail}
    """


def build_comparison_html(spacy_entities, hf_entities):
    def entity_row(e, color):
        return f"""
            <div style="display:flex; justify-content:space-between; padding:6px 10px;
                        border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:#e5e7eb;">{e['text']}</span>
                <span style="color:{color}; font-weight:600; font-size:12px;
                             text-transform:uppercase;">{e['label']}</span>
            </div>
        """

    spacy_rows = "".join(entity_row(e, "#10b981") for e in spacy_entities) or \
        "<p style='color:#6b7280; padding:10px;'>No entities found.</p>"
    hf_rows = "".join(entity_row(e, "#3b82f6") for e in hf_entities) or \
        "<p style='color:#6b7280; padding:10px;'>No entities found.</p>"

    return f"""
        <div style="display:flex; gap:16px; flex-wrap:wrap;">
            <div style="flex:1; min-width:280px; background: rgba(255,255,255,0.02);
                        border: 1px solid rgba(16,185,129,0.3); border-radius: 14px; overflow:hidden;">
                <div style="background:rgba(16,185,129,0.12); color:#10b981; font-weight:700;
                            padding:10px 14px; font-size:13px; text-transform:uppercase;">
                    Your spaCy + Ruler ({len(spacy_entities)} found)
                </div>
                {spacy_rows}
            </div>
            <div style="flex:1; min-width:280px; background: rgba(255,255,255,0.02);
                        border: 1px solid rgba(59,130,246,0.3); border-radius: 14px; overflow:hidden;">
                <div style="background:rgba(59,130,246,0.12); color:#3b82f6; font-weight:700;
                            padding:10px 14px; font-size:13px; text-transform:uppercase;">
                    Hugging Face BERT ({len(hf_entities)} found)
                </div>
                {hf_rows}
            </div>
        </div>
    """


def run_evaluation():
    gold_data = load_gold("data/gold_example.json")
    gold_text = gold_data["text"]
    gold_entities = gold_data["entities"]

    # --- spaCy + Ruler ---
    spacy_entities, spacy_ms = measure_latency_ms(extract_entities, gold_text)
    spacy_scores = precision_recall_f1(gold_entities, spacy_entities)

    spacy_html = build_metrics_html(spacy_scores, spacy_ms)

    # --- Hugging Face ---
    hf_html = ""
    verdict_html = ""

    if HF_AVAILABLE:
        try:
            hf_entities, hf_ms = measure_latency_ms(get_hf_entities, gold_text)
            hf_scores = precision_recall_f1(gold_entities, hf_entities)
            hf_html = build_metrics_html(hf_scores, hf_ms)

            if spacy_scores["f1"] > hf_scores["f1"]:
                winner = "spaCy + Ruler"
                color = "#10b981"
                reason = "It was trained on your exact SKILL/TOOL vocabulary, while BERT uses generic PER/ORG/LOC/MISC labels — not resume skills."
            elif hf_scores["f1"] > spacy_scores["f1"]:
                winner = "Hugging Face BERT"
                color = "#3b82f6"
                reason = "It generalized better on this test sentence."
            else:
                winner = "Both — tie"
                color = "#f59e0b"
                reason = "Both scored equally on this test sentence."

            speed_note = f"spaCy + Ruler is {hf_ms/spacy_ms:.1f}x faster" if spacy_ms > 0 else ""

            verdict_html = f"""
                <div style="margin-top:20px; padding:16px; border-radius:14px;
                            background: {color}15; border: 1px solid {color}44;">
                    <div style="color:{color}; font-weight:800; font-size:15px;">
                        🏆 Winner on this test: {winner}
                    </div>
                    <div style="color:#9ca3af; font-size:13px; margin-top:6px;">
                        {reason} {speed_note}
                    </div>
                </div>
            """
        except Exception as ex:
            hf_html = f"<p style='color:#6b7280;'>Hugging Face model failed to run: {ex}</p>"
    else:
        hf_html = "<p style='color:#6b7280;'>torch/transformers not installed — Hugging Face comparison skipped.</p>"

    gold_text_html = f"<p style='color:#d1d5db; font-size:14px; margin:16px 0;'><b>Test sentence:</b> {gold_text}</p>"

    return f"""
        {gold_text_html}
        <div style="color:#5eead4; font-weight:700; font-size:13px; text-transform:uppercase; margin-bottom:8px;">
            spaCy + Ruler
        </div>
        {spacy_html}
        <div style="color:#3b82f6; font-weight:700; font-size:13px; text-transform:uppercase; margin:20px 0 8px;">
            Hugging Face BERT
        </div>
        {hf_html}
        {verdict_html}
    """


def process_resume(pdf_file):
    if pdf_file is None:
        empty = "<p style='color:#6b7280;'>Upload a resume PDF to get started.</p>"
        return empty, empty, "{}", "", empty

    start = time.perf_counter()
    text, result = analyze_pdf(pdf_file.name)
    elapsed_ms = (time.perf_counter() - start) * 1000

    highlighted = LEGEND_HTML + highlight_text(text, result["entities"])
    sections_html = build_sections_html(result["sections"])
    json_text = json.dumps(result, indent=2)
    latency_text = f"⚡ Extracted in {elapsed_ms:.1f} ms"

    if HF_AVAILABLE:
        try:
            hf_entities = get_hf_entities(text)
        except Exception:
            hf_entities = []
    else:
        hf_entities = []

    comparison_html = build_comparison_html(result["entities"], hf_entities)

    return highlighted, sections_html, json_text, latency_text, comparison_html


with gr.Blocks(theme=gr.themes.Soft(primary_hue="teal"), css=CUSTOM_CSS, title="Resume Skill Extractor") as demo:
    gr.HTML("<div id='title'>Resume Skill Extractor</div>")
    gr.HTML("<div id='subtitle'>Upload a resume — see skills, tools, and experience extracted instantly</div>")

    with gr.Row(elem_id="search-bar-row", equal_height=True):
        with gr.Column(scale=5, min_width=0):
            file_input = gr.File(
                label=None,
                show_label=False,
                file_types=[".pdf"],
                elem_id="file-pill",
                height=40,
            )
        with gr.Column(scale=1, min_width=110):
            extract_btn = gr.Button("Extract", variant="primary", elem_id="extract-pill")

    latency_display = gr.Markdown(elem_id="latency-box")

    with gr.Column(elem_classes="panel"):
        with gr.Tabs():
            with gr.Tab("🎨 Highlighted Resume"):
                highlighted_output = gr.HTML()
            with gr.Tab("📂 Sections"):
                sections_output = gr.HTML()
            with gr.Tab("🧾 JSON"):
                json_output = gr.Code(language="json")
            with gr.Tab("📊 Evaluation"):
                eval_output = gr.HTML(value=run_evaluation())
            with gr.Tab("🤖 spaCy vs HF"):
                comparison_output = gr.HTML()

    extract_btn.click(
        fn=process_resume,
        inputs=[file_input],
        outputs=[highlighted_output, sections_output, json_output, latency_display, comparison_output],
    )

if __name__ == "__main__":
    demo.launch()