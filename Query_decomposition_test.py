import os
import pandas as pd
from datasets import Dataset
from openai import OpenAI
from ragas import evaluate

# DIRECT IMPORTS: Using the base metrics to ensure Type compatibility
from ragas.metrics import Faithfulness, ContextRecall, AnswerCorrectness
from ragas.llms import llm_factory
from ragas.embeddings import HuggingFaceEmbeddings

# 1. SETUP: API Key
# Replace with your actual Groq Key
from dotenv import load_dotenv
load_dotenv()

# 2. LOAD HARD DATASET (10 Multi-Part Queries for Experiment 2)
hard_eval_data = [
    {
        "user_input": "Compare the 2026 range efficiency (mi/kWh) and starting price of the Rivian R2 vs the Tesla Model Y Long Range RWD.",
        "response": "The Rivian R2 starts at $49,985 with a 345-mile range (approx 3.9 mi/kWh), while the Tesla Model Y Premium RWD starts at $46,630 with a 357-mile range (approx 4.0 mi/kWh).",
        "retrieved_contexts": [
            "Tesla Model Y Premium RWD: $46,630, 357 miles range.",
            "Rivian R2 Long Range: $49,985, 345 miles range."
        ],
        "reference": "The Rivian R2 ($49,985) offers 345 miles of range, while the Tesla Model Y Premium RWD ($46,630) offers 357 miles."
    },
    {
        "user_input": "Identify BYD's 2026 export target and the location of their new European factories.",
        "response": "BYD targets 1.6 million overseas sales in 2026 with new plants in Hungary and potentially Spain or Turkey.",
        "retrieved_contexts": [
            "BYD is targeting up to 1.6 million vehicle sales outside China in 2026.",
            "BYD confirmed plans for a major factory in Szeged, Hungary, and is evaluating Spain."
        ],
        "reference": "BYD's 2026 overseas sales target is 1.6 million units, supported by a new plant in Hungary."
    },
    {
        "user_input": "Analyze the frame material and AI software stack in the Rokid AI Glasses Style vs Apple's Project N50 goals.",
        "response": "Rokid AI Style uses thin frames with GPT-5 and DeepSeek; Apple's Project N50 targets 2027 with a camera/mic set similar to Meta Ray-Bans.",
        "retrieved_contexts": [
            "Rokid AI Style uses a multi-LLM stack tapping GPT-5 and DeepSeek.",
            "Apple's Project N50 targets a smart glasses release by 2027."
        ],
        "reference": "Rokid AI Glasses use GPT-5 and DeepSeek, while Apple's Project N50 is a longer-term AI eyewear push."
    },
    {
        "user_input": "Compare Tesla's 2026 capital expenditure (Capex) projection vs BYD's revenue scale in 2025.",
        "response": "Tesla expects Capex to exceed $20 billion in 2026, whereas BYD's 2025 revenue reached a record $116 billion (804 billion CNY).",
        "retrieved_contexts": [
            "Tesla forecasts capital expenditures to exceed $20 billion this year (2026).",
            "BYD's annual revenue reached a record 804 billion CNY ($116 billion USD) in 2025."
        ],
        "reference": "Tesla's 2026 Capex is projected over $20B, while BYD's 2025 revenue was $116B."
    },
    {
        "user_input": "Does every Rivian R2 and 2026 Lucid Gravity support the Tesla Supercharger network natively?",
        "response": "The Rivian R2 has a native NACS port; the 2026 Lucid Gravity also supports NACS integration for Tesla's network.",
        "retrieved_contexts": [
            "Every R2 has a NACS charge port for 21,000 Tesla Superchargers.",
            "The 2026 Lucid Gravity includes NACS integration for the Tesla network."
        ],
        "reference": "Both the Rivian R2 and 2026 Lucid Gravity natively support the Tesla Supercharger network via NACS."
    },
    {
        "user_input": "Who are the core Android XR rivals for Apple and which eyewear brand are they partnering with?",
        "response": "Google and Samsung are the core Android XR rivals, partnering with Warby Parker and Gentle Monster.",
        "retrieved_contexts": [
            "Google is launching Android XR smart glasses co-developed with Warby Parker.",
            "Samsung confirmed a smart glasses launch in 2026 built on Android XR."
        ],
        "reference": "Apple's Android XR rivals include Google and Samsung, partnered with Warby Parker."
    },
    {
        "user_input": "Identify BYD's 2025 profit trend vs their international expansion rate in March 2026.",
        "response": "BYD saw its first profit decline since 2021 in 2025, yet exports rose 65% year-over-year in March 2026.",
        "retrieved_contexts": [
            "BYD reported its first yearly net profit drop since 2021 in 2025.",
            "In March 2026, BYD exported 120,083 vehicles, a 65% increase year-over-year."
        ],
        "reference": "BYD's 2025 profit declined despite a 65% surge in international exports by March 2026."
    },
    {
        "user_input": "Compare the infotainment screen size of the 2026 Lucid Gravity vs the 2026 Tesla Model X.",
        "response": "The Lucid Gravity features a 12.60-inch touchscreen, while the Tesla Model X has a larger 17.00-inch touchscreen.",
        "retrieved_contexts": [
            "Lucid Gravity has a 12.60-inch Touchscreen infotainment system.",
            "Tesla Model X has a 17.00-inch Touchscreen infotainment system."
        ],
        "reference": "The Tesla Model X (17-inch) has a larger infotainment screen than the Lucid Gravity (12.6-inch)."
    },
    {
        "user_input": "What is the weight of the Rokid AI Glasses Style and its primary processor?",
        "response": "The Rokid AI Style frames are 'display-less' and run on a Qualcomm AR1 processor.",
        "retrieved_contexts": [
            "The Rokid AI Glasses Style are thin, display-less frames running on a Qualcomm AR1 processor."
        ],
        "reference": "Rokid AI Style glasses run on the Qualcomm AR1 processor."
    },
    {
        "user_input": "Compare the airbags in the 2026 Lucid Gravity vs the 2026 Tesla Model X.",
        "response": "The Lucid Gravity has 8 airbags, whereas the Tesla Model X is equipped with 12 airbags.",
        "retrieved_contexts": [
            "2026 Lucid Gravity has 8 airbags; 2026 Tesla Model X has 12 airbags."
        ],
        "reference": "The Tesla Model X has more airbags (12) than the Lucid Gravity (8)."
    }
]

dataset = Dataset.from_dict(pd.DataFrame(hard_eval_data))

# 3. INITIALIZE MODELS: OpenAI Bridge to Groq
openai_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"]
)

evaluator_llm = llm_factory(
    model="llama-3.3-70b-versatile", 
    client=openai_client
)

# Initialize embeddings (HuggingFace local model)
# Use 'model' parameter for the latest library compatibility
evaluator_embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")

# 4. EXECUTE TEST 2
print("🚀 Starting Experiment 2: Hard Queries Evaluation...")

# Initialize metrics individually
m1 = Faithfulness(llm=evaluator_llm)
m2 = ContextRecall(llm=evaluator_llm)
m3 = AnswerCorrectness(llm=evaluator_llm, embeddings=evaluator_embeddings)

# Pack into a list for evaluate()
metrics_list = [m1, m2, m3]

# Run the evaluation
result = evaluate(
    dataset=dataset,
    metrics=metrics_list
)

# 5. RESULTS
print("\n📊 Experiment 2 Results:")
df_results = result.to_pandas()

# Clean display of results
cols = [c for c in ['user_input', 'faithfulness', 'context_recall', 'answer_correctness'] if c in df_results.columns]
print(df_results[cols])

# Save results for your project documentation
df_results.to_csv("experiment_2_hard_queries.csv", index=False)
print("\n✅ Evaluation complete. Data saved to 'experiment_2_hard_queries.csv'")