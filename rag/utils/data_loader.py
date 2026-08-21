import os
import json
from rag.utils.scraper import collect_market_data
from rag.utils.gov_sources import fetch_gov_data

def build_dataset(query=None):
    # 1. Fetch fresh data
    news = collect_market_data(query=query)
    gov = fetch_gov_data()
    data = news + gov

    # 2. ARCHITECT FIX: Dynamic Path Resolution
    # This finds the directory where THIS file (data_loader.py) lives
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    # Move up one level to reach the 'rag' folder
    rag_dir = os.path.dirname(current_dir)
    # Define the target data folder
    data_dir = os.path.join(rag_dir, "data")

    # 3. Create the 'data' folder if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 4. Define the final file path
    file_path = os.path.join(data_dir, "market_data.json")

    # 5. Save the data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"--- Architect: Knowledge base updated successfully at: {file_path} ---")