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
    {
        "question": "What is the battery range of the 2026 Tesla Model 3?",
        "answer": "The 2026 Tesla Model 3 has a range of 363 miles.",
        "contexts": ["The 2026 Model 3 Premium RWD delivers 363 miles of EPA-estimated range."],
        "ground_truth": "The 2026 Model 3 Premium RWD has an EPA-estimated range of 363 miles."
    },
    {
        "question": "Who are the top competitors for Apple's N50 smart glasses?",
        "answer": "Apple's smart glasses compete with Meta and Google products.",
        "contexts": ["Apple N50 glasses aim to outdo rivals like Meta and Google."],
        "ground_truth": "The main competitors are Meta (Ray-Ban Meta) and Google."
    }
]

df = pd.DataFrame(eval_data)
dataset = Dataset.from_dict(df)

# 3. THE MODELS: Wrapping Langchain for Ragas
# We use llama-3.3-70b-versatile as it's the current active model
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
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