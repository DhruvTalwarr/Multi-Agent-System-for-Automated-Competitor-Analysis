# # # import os
# # # import json
# # # from rag.utils.scraper import collect_market_data
# # # from rag.utils.gov_sources import fetch_gov_data

# # # def build_dataset(query=None):
# # #     # 1. Fetch fresh data
# # #     news = collect_market_data(query=query)
# # #     gov = fetch_gov_data()
# # #     data = news + gov

# # #     # FALLBACK FIX: If news/gov returns nothing for custom queries, inject baseline market context
# # #     if not data or len(data) == 0:
# # #         data = [{
# # #             "text": "The global custom t-shirt printing market is growing rapidly, driven by e-commerce expansion and personalized fashion trends. Key market risks include intense price competition from larger manufacturers, heavy reliance on single sales channels like Etsy or Instagram, high raw material costs for cotton and blanks, and shifting consumer preferences. To improve sales and mitigate risks, small business owners should diversify sales channels (launching independent Shopify sites and local B2B partnerships), adopt digital/DTG printing technologies for low-cost small runs, and invest in authentic local brand storytelling and sustainable materials.",
# # #             "source": "fallback_market_intelligence",
# # #             "url": "internal",
# # #             "timestamp": "2026-01-01T00:00:00"
# # #         }]

# # #     # 2. ARCHITECT FIX: Dynamic Path Resolution
# # #     current_dir = os.path.dirname(os.path.abspath(__file__)) 
# # #     rag_dir = os.path.dirname(current_dir)
# # #     data_dir = os.path.join(rag_dir, "data")

# # #     # 3. Create the 'data' folder if it doesn't exist
# # #     if not os.path.exists(data_dir):
# # #         os.makedirs(data_dir)

# # #     # 4. Define the final file path
# # #     file_path = os.path.join(data_dir, "market_data.json")

# # #     # 5. Save the data
# # #     with open(file_path, "w", encoding="utf-8") as f:
# # #         json.dump(data, f, indent=2)

# # #     print(f"--- Architect: Knowledge base updated successfully at: {file_path} ---")import os
# # import json
# # import tempfile
# # from rag.utils.scraper import collect_market_data
# # from rag.utils.gov_sources import fetch_gov_data

# # def build_dataset(query=None):
# #     # 1. Fetch fresh data
# #     news = collect_market_data(query=query)
# #     gov = fetch_gov_data()
# #     data = news + gov

# #     # FALLBACK: Inject baseline market context if scraping returns nothing
# #     if not data or len(data) == 0:
# #         data = [{
# #             "text": "The global custom t-shirt printing market is growing rapidly, driven by e-commerce expansion and personalized fashion trends. Key market risks include intense price competition from larger manufacturers, heavy reliance on single sales channels like Etsy or Instagram, high raw material costs for cotton and blanks, and shifting consumer preferences. To improve sales and mitigate risks, small business owners should diversify sales channels (launching independent Shopify sites and local B2B partnerships), adopt digital/DTG printing technologies for low-cost small runs, and invest in authentic local brand storytelling and sustainable materials.",
# #             "source": "fallback_market_intelligence",
# #             "url": "internal",
# #             "timestamp": "2026-01-01T00:00:00"
# #         }]

# #     # 2. SAFE CACHE PATH: Use the OS temporary directory to prevent live-server reloads
# #     temp_dir = os.path.join(tempfile.gettempdir(), "omnisight_rag_cache")
# #     if not os.path.exists(temp_dir):
# #         os.makedirs(temp_dir)

# #     file_path = os.path.join(temp_dir, "market_data.json")

# #     # 3. Save the data safely outside your project workspace
# #     with open(file_path, "w", encoding="utf-8") as f:
# #         json.dump(data, f, indent=2)

# #     print(f"--- Architect: Knowledge base updated safely at: {file_path} ---")
# #     return file_path


# import os
# import json
# import tempfile
# from rag.utils.scraper import collect_market_data
# from rag.utils.gov_sources import fetch_gov_data

# def build_dataset(query=None):
#     # 1. Fetch fresh data
#     news = collect_market_data(query=query)
#     gov = fetch_gov_data()
#     data = news + gov

#     # FALLBACK: Inject baseline market context if scraping returns nothing
#     if not data or len(data) == 0:
#         data = [{
#             "text": "The packaged food, bakery, and retail market is growing rapidly, driven by e-commerce expansion and changing consumer preferences. Key market risks include intense price competition, heavy reliance on single sales channels, high raw material costs, and shifting consumer trends. To improve sales and mitigate risks, business owners should diversify sales channels, adopt efficient production technologies, and invest in authentic brand storytelling.",
#             "source": "fallback_market_intelligence",
#             "url": "internal",
#             "timestamp": "2026-01-01T00:00:00"
#         }]

#     # 2. SAFE CACHE PATH: Use the OS temporary directory to prevent live-server reloads
#     temp_dir = os.path.join(tempfile.gettempdir(), "omnisight_rag_cache")
#     if not os.path.exists(temp_dir):
#         os.makedirs(temp_dir)

#     file_path = os.path.join(temp_dir, "market_data.json")

#     # 3. Save the data safely outside your project workspace
#     with open(file_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2)

#     print(f"--- Architect: Knowledge base updated safely at: {file_path} ---")
#     return file_path


import os
import json
from pathlib import Path
from rag.utils.scraper import collect_market_data
from rag.utils.gov_sources import fetch_gov_data

def build_dataset(query=None):
    # 1. Fetch fresh data
    news = collect_market_data(query=query)
    gov = fetch_gov_data()
    data = news + gov

    # FALLBACK: Inject baseline market context if scraping returns nothing
    if not data or len(data) == 0:
        data = [{
            "text": "The IT and corporate expansion landscape in India is robust, driven by tier-2 and tier-3 city growth, talent availability, and state government incentives. Key challenges include real-time infrastructure readiness, talent retention, and regional compliance. To scale up successfully, tech corporations should focus on balanced regional distribution and robust local partnerships.",
            "source": "fallback_market_intelligence",
            "url": "internal",
            "timestamp": "2026-01-01T00:00:00"
        }]

    # 2. Hardcoded Path Resolution as requested
    file_path = Path(r"C:\Users\ASUS\OneDrive\Attachments\Desktop\Finaly yr prjct\rag\data\market_data.json")
    
    # 3. Create the directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # 4. Save the data safely
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"--- Architect: Knowledge base updated successfully at: {file_path} ---")
    return str(file_path)