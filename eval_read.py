import pandas as pd

# Load your saved results
df = pd.read_csv('project_evaluation_results.csv')

# Calculate the averages
summary = {
    "Average Faithfulness": df['faithfulness'].mean(),
    "Average Recall": df['context_recall'].mean(),
    "Average Correctness": df['answer_correctness'].mean()
}

print("📋 PROJECT EVALUATION SUMMARY:")
for metric, score in summary.items():
    print(f"{metric}: {score:.2f}")