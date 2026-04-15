from pathlib import Path
import json

from rag.rag_pipeline import RAGPipeline
from rag.evaluator import precision_at_k, recall_at_k, f1_score, extract_entities


# ------------------ PATH ------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "market_data.json"
EVAL_FILE = BASE_DIR / "data" / "eval_dataset.json"


# ------------------ INIT ------------------

rag = RAGPipeline()
rag.initialize(str(DATA_FILE))


# ------------------ SINGLE TEST ------------------

query = "Compare Zomato vs Swiggy"

print("\n================= SINGLE QUERY =================")
result = rag.generate_response(query)

print("\nAnswer:\n", result["answer"])


# ------------------ EVALUATION ------------------

print("\n================= EVALUATION =================")

with open(EVAL_FILE, "r") as f:
    dataset = json.load(f)


for item in dataset:
    query = item["query"]
    ground_truth = item["ground_truth"]

    result = rag.generate_response(query)

    answer = result["answer"]

    predicted_entities = extract_entities(answer)
    predicted_entities = list(set(predicted_entities))

    p = precision_at_k(predicted_entities, ground_truth)
    r = recall_at_k(predicted_entities, ground_truth)
    f1 = f1_score(p, r)

    print("\n-----------------------------------")
    print(f"Query: {query}")
    print(f"Predicted: {predicted_entities}")
    print(f"Ground Truth: {ground_truth}")
    print(f"Precision: {p:.2f}")
    print(f"Recall: {r:.2f}")
    print(f"F1 Score: {f1:.2f}")