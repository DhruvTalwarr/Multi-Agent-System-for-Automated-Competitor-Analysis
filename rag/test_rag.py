from pathlib import Path

from rag.rag_pipeline import RAGPipeline

DATA_FILE = Path(__file__).resolve().parent / "data" / "market_data.json"

rag = RAGPipeline()

rag.initialize(str(DATA_FILE))

query = "Compare Zomato vs Swiggy"

response = rag.generate_response(query)

print(response)
