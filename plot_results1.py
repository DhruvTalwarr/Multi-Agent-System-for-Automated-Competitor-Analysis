import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Setup Data from your results
metrics = ['Faithfulness', 'Context Recall', 'Answer Correctness']
scores = [0.89, 1.00, 0.81] # Based on your terminal output

# 2. Create Plot
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")
colors = ['#4e79a7', '#59a14f', '#f28e2b'] # Professional blue, green, orange

barplot = sns.barplot(x=metrics, y=scores, palette=colors)

# 3. Add Labels
plt.title('Automated Competitor Intelligence:  Performance', fontsize=16, pad=20)
plt.ylabel('Score (0.0 - 1.0)', fontsize=12)
plt.ylim(0, 1.1) # Leave space for text labels

# Add the actual numbers on top of the bars
for i, score in enumerate(scores):
    barplot.text(i, score + 0.02, f'{score:.2f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

# 4. Save and Show
plt.tight_layout()
plt.savefig('system_performance.png')
print("✅ Graph saved as 'system_performance.png'. You can now add this to your presentation!")
plt.show()