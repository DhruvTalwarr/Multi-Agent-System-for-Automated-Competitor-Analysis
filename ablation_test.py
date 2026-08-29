import os
import pandas as pd
import time
from openai import OpenAI

# 1. SETUP
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.environ["GROQ_API_KEY"])

# 2. TEST CASE (A complex, multi-part query)
test_query = "Compare Tesla's 2026 Capex vs BYD's 2025 Revenue."

# 3. COMPONENT 1: The "Full" System Logic (Decomposition)
def full_system_process(query):
    print("🔍 Running Full System (with Decomposition)...")
    # In your real code, this would call your decomposition function
    sub_queries = ["What is Tesla's 2026 Capex?", "What is BYD's 2025 revenue?"]
    # Simulate finding two distinct facts
    contexts = ["Tesla 2026 Capex: $20B", "BYD 2025 Revenue: $116B"]
    return contexts

# 4. COMPONENT 2: The "Ablated" System Logic (No Decomposition)
def ablated_system_process(query):
    print("⚠️ Running Ablated System (NO Decomposition)...")
    # Without decomposition, the search often only finds the first primary entity
    contexts = ["Tesla 2026 Capex: $20B"] # Failed to find BYD because query was too broad
    return contexts

# 5. EVALUATION FUNCTION
# def evaluate_ablation(system_type, contexts):
# 5. EVALUATION FUNCTION (Updated for 2026 Model IDs)
def evaluate_ablation(system_type, contexts):
    prompt = f"""
    Based on the contexts provided, can you answer: '{test_query}'?
    Contexts: {contexts}
    Answer ONLY 'Complete' if both parts are answered, or 'Incomplete' if only one part or no parts are answered.
    """
    try:
        response = client.chat.completions.create(
            # Using Llama 3.1 8B (The current standard for fast, small-model tasks)
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"
# 6. EXECUTION
full_ctx = full_system_process(test_query)
ablated_ctx = ablated_system_process(test_query)

full_result = evaluate_ablation("Full", full_ctx)
ablated_result = evaluate_ablation("Ablated", ablated_ctx)

# 7. RESULTS
ablation_report = {
    "Configuration": ["Full System (with Decomposition)", "Ablated System (Raw Query Only)"],
    "Contexts Found": [len(full_ctx), len(ablated_ctx)],
    "Answer Completeness": [full_result, ablated_result]
}

df_ablation = pd.DataFrame(ablation_report)
print("\n📊 ABLATION STUDY RESULTS")
print("-" * 60)
print(df_ablation)

df_ablation.to_csv("Ablation_Study_Results.csv", index=False)