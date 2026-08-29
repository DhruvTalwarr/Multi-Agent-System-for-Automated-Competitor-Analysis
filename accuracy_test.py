import pandas as pd
import os

# 1. GROUND TRUTH: The "Gold Standard" Competitors (Updated for 2026)
# These are verified market leaders your AI should be able to identify.
ground_truth_map = {
    "Tesla": ["BYD", "Rivian", "Lucid", "Xiaomi", "Volkswagen", "Hyundai", "Geely"],
    "BYD": ["Tesla", "Geely", "Xiaomi", "Li Auto", "Changan", "NIO"],
    "NVIDIA": ["AMD", "Intel", "Broadcom", "Google (TPU)", "AWS (Inferentia)", "Huawei"],
    "Apple Smart Glasses": ["Meta", "Google", "Samsung", "Xreal", "Rokid", "RayNeo"],
    "Rivian": ["Tesla", "Ford", "General Motors", "Lucid", "Amazon (EDV)"]
}

def evaluate_identification(company, predictions):
    """Calculates IR metrics: Precision, Recall, and F1-Score."""
    truth = set(ground_truth_map.get(company, []))
    preds = set(predictions)
    
    tp = len(preds.intersection(truth))  # Correctly identified
    fp = len(preds - truth)              # Hallucinations/Irrelevant
    fn = len(truth - preds)              # Missed competitors
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "Target": company,
        "TP": tp, "FP": fp, "FN": fn,
        "Precision": round(precision, 2),
        "Recall": round(recall, 2),
        "F1_Score": round(f1, 2)
    }

# 2. EXPERIMENT DATA: Enter your AI's actual outputs here
# These are samples. Replace them with the data from your Agent.
experiment_outputs = [
    ("Tesla", ["BYD", "Rivian", "Lucid", "Xiaomi", "Ford"]), 
    ("Apple Smart Glasses", ["Meta", "Google", "Samsung", "Xreal", "Microsoft"]),
    ("NVIDIA", ["AMD", "Intel", "Broadcom", "Huawei", "Cerebras"])
]

# 3. GENERATE RESULTS
results_list = []
for company, preds in experiment_outputs:
    results_list.append(evaluate_identification(company, preds))

df_results = pd.DataFrame(results_list)

# 4. FORMAT FOR AKTU/PSIT REPORT
# We add a Mean row at the bottom for the "Final Analysis"
mean_vals = {
    "Target": "AVERAGE PERFORMANCE",
    "Precision": df_results["Precision"].mean(),
    "Recall": df_results["Recall"].mean(),
    "F1_Score": df_results["F1_Score"].mean()
}
df_final = pd.concat([df_results, pd.DataFrame([mean_vals])], ignore_index=True)

# 5. SAVE & DISPLAY
print("\n📊 EXPERIMENT 3: COMPETITOR IDENTIFICATION ACCURACY")
print("-" * 65)
print(df_final[['Target', 'Precision', 'Recall', 'F1_Score']])

# Save in professional CSV format
df_final.to_csv("Experiment3_Accuracy_Metrics.csv", index=False)
print(f"\n✅ Results saved to: {os.getcwd()}\\Experiment3_Accuracy_Metrics.csv")