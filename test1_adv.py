import os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
# Updated imports for Ragas 0.4+ / 1.0
from ragas.metrics import Faithfulness, ContextRecall, AnswerCorrectness
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# 1. SETUP: API Key
from dotenv import load_dotenv
load_dotenv()

# 2. DATASET
eval_data = [
    # --- AUTOMOTIVE SECTOR (Real-time 2026 Stats) ---
    {
        "question": "Compare the 2026 range efficiency of the Rivian R2 vs the Tesla Model Y Long Range RWD.",
        "answer": "The Rivian R2 achieves 3.9 mi/kWh (345 miles range), whereas the Tesla Model Y Long Range RWD is slightly more efficient at 4 mi/kWh (357 miles range).",
        "contexts": ["The Rivian R2 Standard offers 345 miles of range with an efficiency of 3.9 mi/kWh. The Tesla Model Y Long Range RWD is EPA-rated for 357 miles at 4 mi/kWh."],
        "ground_truth": "The Rivian R2 has an efficiency of 3.9 mi/kWh (345 miles), while the Tesla Model Y Long Range RWD is slightly higher at 4 mi/kWh (357 miles)."
    },
    {
        "question": "What is BYD's global export target for 2026 and how does it compare to 2025?",
        "answer": "BYD has raised its 2026 export target to 1.5 - 1.6 million units, nearly doubling the 2025 goal of 900,000 to 1 million units.",
        "contexts": ["BYD indicated to analysts that exports would reach 1.5 million units in 2026, up from a 1.3 million target earlier. This follows an expected 900k-1M units in 2025."],
        "ground_truth": "BYD's 2026 export target is 1.5 to 1.6 million units, a significant increase from the 2025 target of 900,000 to 1,000,000 units."
    },
    {
        "question": "How does the starting price of the 2026 Lucid Gravity compare to the Tesla Model X in the UK market?",
        "answer": "The Lucid Gravity is roughly £13,000 cheaper, starting at £85,600 compared to the Model X at £98,600.",
        "contexts": ["Lucid Gravity starts at £85,600, while the Tesla Model X costs £98,600, a difference of approximately £13,000."],
        "ground_truth": "The Lucid Gravity (£85,600) is approximately £13,000 cheaper than the Tesla Model X (£98,600)."
    },
    {
        "question": "Which company holds the title of the world's most valuable EV brand in 2026, and what is its valuation?",
        "answer": "Tesla remains the world's most valuable EV brand with a valuation exceeding $1.6 trillion.",
        "contexts": ["Tesla remains the world's most valuable EV brand, exceeding $1.6 trillion in market capitalization in the 2026 electric landscape."],
        "ground_truth": "Tesla is the most valuable EV brand globally, with a market capitalization exceeding $1.6 trillion."
    },
    {
        "question": "What are Rivian's projected unit deliveries for the year 2026?",
        "answer": "Rivian's projected deliveries for 2026 are under 200,000 units.",
        "contexts": ["Rivian remains distant in volume, with projected 2026 deliveries under 200,000 units."],
        "ground_truth": "Rivian is expected to deliver fewer than 200,000 units in 2026."
    },

    # --- TECH & WEARABLES (2026 Strategy) ---
    {
        "question": "What material is Apple using for its N50 smart glasses to differentiate from plastic competitors?",
        "answer": "Apple is using 'luxurious' acetate for its N50 frames, whereas most competitors use standard plastic.",
        "contexts": ["Apple plans to use acetate for its N50 frames to appear more durable and luxurious than the standard plastic used by many brands."],
        "ground_truth": "Apple is using high-end acetate for the N50 frames to provide a more durable and premium feel compared to standard plastic competitors."
    },
    {
        "question": "Identify the core AI software stack used in the Rokid AI Glasses Style launched in 2026.",
        "answer": "The Rokid AI Glasses Style uses a multi-LLM stack featuring both GPT-5 and DeepSeek.",
        "contexts": ["Rokid AI Glasses Style launched in Jan 2026 uses a multi-LLM AI stack that taps both ChatGPT GPT-5 and DeepSeek."],
        "ground_truth": "The Rokid AI Glasses use a combination of GPT-5 and DeepSeek for their AI capabilities."
    },
    {
        "question": "Which tech company is partnering with Warby Parker for its 2026 smart glasses release?",
        "answer": "Google and Samsung are partnering with Warby Parker for their Android XR smart glasses.",
        "contexts": ["Google and Samsung are leaning on Warby Parker for frames for their 2026 smart glasses launch built on Android XR."],
        "ground_truth": "Google and Samsung are collaborating with Warby Parker for their smart glasses frames."
    },

    # --- INFRASTRUCTURE & FINANCE ---
    {
        "question": "Does every Rivian R2 come with access to the Tesla Supercharger network natively?",
        "answer": "Yes, every Rivian R2 is equipped with a NACS charge port, allowing access to over 21,000 Tesla Superchargers.",
        "contexts": ["Every R2 has a NACS charge port, allowing you to charge at over 21,000 Tesla Superchargers across the US and Canada."],
        "ground_truth": "All Rivian R2 vehicles include a NACS port for native access to the Tesla Supercharger network."
    },
    {
        "question": "What is the expected capital expenditure trend for BYD in late 2025 and 2026?",
        "answer": "BYD's capital expenditure is expected to decline in 2026 as production capacity meets global demand.",
        "contexts": ["BYD expects capital expenditure (capex) to decline in late 2025 and more pronouncedly in 2026 as capacity reaches sustainable levels."],
        "ground_truth": "BYD's capex is projected to decrease in 2026 because vehicle and battery production capacity has reached sustainable global levels."
    }
]

df = pd.DataFrame(eval_data)
dataset = Dataset.from_dict(df)

# 3. THE MODELS: Wrapping Langchain for Ragas
# We use openai/gpt-oss-120b as it's the current active model
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
evaluator_llm = LangchainLLMWrapper(llm)

# Fix for Embeddings (HuggingFace avoids OpenAI Key requirement)
hf_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
evaluator_embeddings = LangchainEmbeddingsWrapper(hf_embeddings)

# 4. EXECUTE: Pass the metrics as objects
print("🚀 Starting Evaluation (Stability Mode)...")
result = evaluate(
    dataset=dataset,
    metrics=[
        Faithfulness(), 
        ContextRecall(), 
        AnswerCorrectness()
    ],
    llm=evaluator_llm,
    embeddings=evaluator_embeddings
)
# 5. RESULTS: Let's see what the AI found!
print("\n📊 Evaluation Results:")
df_results = result.to_pandas()

# Ragas 1.0 uses 'user_input' instead of 'question'
# This logic checks for both so it never crashes again
cols_to_show = []
for col in ['user_input', 'question', 'faithfulness', 'context_recall', 'answer_correctness']:
    if col in df_results.columns:
        cols_to_show.append(col)

print(df_results[cols_to_show])

# Save to CSV for your PSIT project presentation
df_results.to_csv("project_evaluation_results.csv", index=False)
print("\n✅ Success! Results saved to 'project_evaluation_results.csv'")