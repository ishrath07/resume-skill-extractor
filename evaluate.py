import json

from src.ner import extract_entities
from src.metrics import precision_recall_f1, measure_latency_ms


def load_gold(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    gold_data = load_gold("data/gold_example.json")
    gold_text = gold_data["text"]
    gold_entities = gold_data["entities"]

    predicted_entities, elapsed_ms = measure_latency_ms(extract_entities, gold_text)

    scores = precision_recall_f1(gold_entities, predicted_entities)

    print(f"Text: {gold_text}")
    print()
    print(f"Precision: {scores['precision']}")
    print(f"Recall:    {scores['recall']}")
    print(f"F1:        {scores['f1']}")
    print(f"Latency:   {elapsed_ms:.2f} ms")
    print()
    print(f"True positives: {scores['true_positives']} / gold: {scores['gold_count']} / predicted: {scores['predicted_count']}")


if __name__ == "__main__":
    main()