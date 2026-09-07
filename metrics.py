import time


def normalize(text):
    """Lowercase and collapse extra spaces, so 'Python ' matches 'python'."""
    return " ".join(text.lower().split())


def precision_recall_f1(gold_entities, predicted_entities):
    """
    gold_entities and predicted_entities are lists of dicts like:
        {"text": "Python", "label": "SKILL"}

    A match = same text (ignoring case/extra spaces) AND same label.
    """
    gold_set = {(normalize(e["text"]), e["label"]) for e in gold_entities}
    predicted_set = {(normalize(e["text"]), e["label"]) for e in predicted_entities}

    true_positives = gold_set & predicted_set

    precision = len(true_positives) / len(predicted_set) if predicted_set else 0.0
    recall = len(true_positives) / len(gold_set) if gold_set else 0.0

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "true_positives": len(true_positives),
        "gold_count": len(gold_set),
        "predicted_count": len(predicted_set),
    }


def measure_latency_ms(func, *args, **kwargs):
    """Runs func(*args, **kwargs) once and returns (result, elapsed_ms)."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result, elapsed_ms


if __name__ == "__main__":
    gold = [
        {"text": "Python", "label": "SKILL"},
        {"text": "FastAPI", "label": "SKILL"},
        {"text": "machine learning", "label": "SKILL"},
    ]
    predicted = [
        {"text": "Python", "label": "SKILL"},
        {"text": "Java", "label": "SKILL"},
        {"text": "FastAPI", "label": "SKILL"},
    ]
    print(precision_recall_f1(gold, predicted))
    # Should print precision: 0.667, recall: 0.667 (matches the tiny math example from Phase 3)