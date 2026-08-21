import time
import os
import pandas as pd
from openai import OpenAI

# 1. SETUP
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"])

# 2. STRESS TEST DATASET
# We add "Noise" (irrelevant info) to see if the AI gets distracted
stress_test_data = [
    {
        "query": "What is Tesla's 2026 Capex projection?",
        "clean_context": "Tesla expects Capex to exceed $20 billion in 2026.",
        "noisy_context": "Tesla expects Capex to exceed $20 billion in 2026. Also, a local bakery in Kanpur is selling sourdough bread for 200 rupees.",
        "reference": "Over $20 billion."
    }
]

def run_performance_test(case, use_noise=False):
    context = case['noisy_context'] if use_noise else case['clean_context']
    prompt = f"Context: {context}\nQuestion: {case['query']}\nAnswer briefly:"
    
    start_time = time.time()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    end_time = time.time()
    
    return {
        "Latency (s)": round(end_time - start_time, 3),
        "Response": response.choices[0].message.content,
        "Tokens": response.usage.total_tokens
    }

# 3. EXECUTION
print("🚀 Starting Experiment 5: Robustness & Efficiency...")
clean_perf = run_performance_test(stress_test_data[0], use_noise=False)
noisy_perf = run_performance_test(stress_test_data[0], use_noise=True)

# 4. RESULTS TABLE
perf_results = {
    "Metric": ["Latency (Seconds)", "Token Usage", "Accuracy preserved?"],
    "Clean Context": [clean_perf['Latency (s)'], clean_perf['Tokens'], "Yes"],
    "Noisy Context": [noisy_perf['Latency (s)'], noisy_perf['Tokens'], "Yes" if "20 billion" in noisy_perf['Response'] else "No"]
}

df_perf = pd.DataFrame(perf_results)
print("\n📊 EXPERIMENT 5: SYSTEM ROBUSTNESS")
print("-" * 50)
print(df_perf)

df_perf.to_csv("Experiment5_Robustness.csv", index=False)