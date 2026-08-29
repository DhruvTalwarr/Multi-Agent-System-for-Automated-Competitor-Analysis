# # # import os
# # # import json
# # # import time
# # # from pathlib import Path
# # # from langchain_groq import ChatGroq
# # # from state import AgentState
# # # import yfinance as yf

# # # # --- INTEGRATION: Gaurav's RAG & Scraper Modules ---
# # # from rag.rag_pipeline import RAGPipeline
# # # from rag.utils.data_loader import build_dataset  
# # # from rag.retriever import has_query_evidence    

# # # # --- CONFIGURATION ---
# # # smart_llm = ChatGroq(
# # #     model="openai/gpt-oss-120b", 
# # #     temperature=0.3,
# # #     groq_api_key=os.getenv("GROQ_API_KEY")
# # # )

# # # DATA_FILE = Path(__file__).resolve().parent / "rag" / "data" / "market_data.json"
# # # rag_system = RAGPipeline()

# # # # --- HELPER FUNCTIONS ---

# # # def classify_intent(query: str) -> str:
# # #     """Classifies incoming query to prevent forcing business reports on general requests."""
# # #     query_lower = query.lower()
    
# # #     # STRICT Financial Check: Only trigger if looking up an actual public stock symbol or explicit ticker terms
# # #     if any(k in query_lower for k in ["stock price", "ticker", "market cap", "pe ratio", "nse:", "bse:"]):
# # #         return "FINANCIAL_ANALYSIS"
        
# # #     # Full Strategic / Business Report Intent
# # #     if any(k in query_lower for k in ["swot", "business plan", "competitor analysis", "strategic recommendation", "market research", "executive summary", "revenue", "sales", "printing", "business"]):
# # #         return "BUSINESS_REPORT"
        
# # #     # File Summaries, Resumes, or General Questions
# # #     return "INFORMATIONAL_SUMMARY"

# # # def get_financial_metrics(query: str):
# # #     """
# # #     Architect Tool: Smart Ticker Discovery for Global and Indian Markets.
# # #     """
# # #     try:
# # #         print(f"--- Architect: Discovering ticker for '{query}'... ---")
# # #         search_term = " ".join(query.split()[:2])
# # #         search = yf.Search(search_term, max_results=3)
        
# # #         if not search.quotes:
# # #             return "Financial data: No public ticker discovered for this entity."
            
# # #         quotes = search.quotes
# # #         best_quote = quotes[0]
# # #         for q in quotes:
# # #             if any(exch in q.get('exchange', '') for exch in ['NMS', 'NYQ', 'NGM']): # US Tech Exchanges
# # #                 best_quote = q
# # #                 break
        
# # #         ticker = best_quote['symbol']
# # #         stock = yf.Ticker(ticker)
# # #         info = stock.info
        
# # #         metrics = {
# # #             "Entity Name": info.get("longName", "N/A"),
# # #             "Ticker": ticker,
# # #             "Exchange": info.get("exchange", "N/A"),
# # #             "Market Cap": info.get("marketCap", "N/A"),
# # #             "Total Revenue": info.get("totalRevenue", "N/A"),
# # #             "Trailing P/E": info.get("trailingPE", "N/A"),
# # #             "Debt to Equity": info.get("debtToEquity", "N/A"),
# # #             "Current Price": f"{info.get('currentPrice', 'N/A')} {info.get('currency', 'USD')}",
# # #             "52 Week High": info.get("fiftyTwoWeekHigh", "N/A")
# # #         }
# # #         return metrics
# # #     except Exception as e:
# # #         return f"Financial data retrieval failed: {str(e)}"

# # # # --- AGENT NODES ---

# # # def planner_agent(state: AgentState):
# # #     query = state['messages'][-1]
# # #     print(f"\n[PLANNER]: Analyzing query intent for: {query[:60]}...")
# # #     return {
# # #         "plan": f"Execute targeted research for: {query}",
# # #         "messages": ["Planner: Task categorized. Initiating research."]
# # #     }

# # # def researcher_agent(state: AgentState):
# # #     """
# # #     Architect Role: Live Search & Context Integrator.
# # #     Clears stale context if the query shifts industry or topic.
# # #     """
# # #     query = state['messages'][0]
# # #     intent = classify_intent(query)
# # #     needs_update = True

# # #     # 1. Stale Context Prevention: Clear local cache if query changes topic
# # #     if DATA_FILE.exists():
# # #         with open(DATA_FILE, "r", encoding="utf-8") as f:
# # #             local_content = f.read().lower()
        
# # #         query_terms = [w.lower() for w in query.split() if len(w) > 3]
# # #         term_match = any(term in local_content for term in query_terms)

# # #         if not term_match or not has_query_evidence(query, local_content):
# # #             print(f"--- Architect: Topic shift or stale data detected. Clearing cache... ---")
# # #             try:
# # #                 os.remove(DATA_FILE)
# # #             except Exception as e:
# # #                 print(f"--- Architect: Warning: Could not delete stale file: {e} ---")
# # #         else:
# # #             print(f"--- Architect: Relevant local context found. ---")
# # #             needs_update = False

# # #     if needs_update:
# # #         print(f"--- Architect: Triggering LIVE SCRAPE for '{query[:40]}'... ---")
# # #         build_dataset(query=query)
# # #         rag_system.initialize(str(DATA_FILE))
# # #     else:
# # #         if not rag_system._initialized:
# # #             rag_system.initialize(str(DATA_FILE))

# # #     # 2. Financial API Execution (only for financial queries)
# # #     fin_data = get_financial_metrics(query) if intent == "FINANCIAL_ANALYSIS" else "N/A (Not a financial query)"

# # #     # 3. RAG Retrieval
# # #     rag_response = rag_system.generate_response(query)
    
# # #     combined_context = f"REAL-TIME FINANCIAL METRICS:\n{json.dumps(fin_data, indent=2) if isinstance(fin_data, dict) else fin_data}\n\nRETRIEVED CONTEXT & DOCUMENTS:\n{rag_response}"
    
# # #     return {
# # #         "research_data": combined_context, 
# # #         "messages": ["Researcher: Context retrieved."]
# # #     }

# # # def report_generator_agent(state: AgentState):
# # #     research = state["research_data"]
# # #     query = state['messages'][0]
# # #     intent = classify_intent(query)
    
# # #     # -------------------------------------------------------------
# # #     # ROUTE 1: Informational Query / Document Summary / Resume Overview
# # #     # -------------------------------------------------------------
# # #     if intent == "INFORMATIONAL_SUMMARY":
# # #         prompt = f"""
# # #         You are a helpful and precise AI Assistant.
        
# # #         USER REQUEST: {query}
        
# # #         PROVIDED CONTEXT / ATTACHED FILE:
# # #         {research}
        
# # #         STRICT INSTRUCTIONS:
# # #         1. Direct Answer: Answer the user's specific query clearly and directly based strictly on the provided context.
# # #         2. DO NOT format this as a business strategy, corporate hiring recommendation, investor proposal, or SWOT report.
# # #         3. Do NOT invent external metrics, financial budgets, or market forecasts.
# # #         4. Use clean Markdown formatting (bullet points and bold subheadings).
# # #         """
        
# # #     # -------------------------------------------------------------
# # #     # ROUTE 2: Financial & Valuation Analysis
# # #     # -------------------------------------------------------------
# # #     elif intent == "FINANCIAL_ANALYSIS":
# # #         prompt = f"""
# # #         You are a Senior Equity Research Analyst.
# # #         USER REQUEST: {query}
        
# # #         RESEARCH DATA:
# # #         {research}
        
# # #         FORMAT YOUR RESPONSE AS:
# # #         1. Financial & Valuation Overview
# # #         2. Key Metrics Comparison Table
# # #         3. Market Risk & Investment Conclusion
# # #         """
        
# # #     # -------------------------------------------------------------
# # #     # ROUTE 3: Explicit Strategic / Business Decision Request
# # #     # -------------------------------------------------------------
# # #     else:
# # #         prompt = f"""
# # #         You are an expert Small Business and Commercial Growth Consultant.
# # #         USER REQUEST: {query}
        
# # #         RESEARCH DATA:
# # #         {research}
        
# # #         STRICT FORMATTING & CONTENT INSTRUCTIONS:
# # #         1. Context Adherence: Analyze the user's specific business type mentioned in the request (e.g., retail, local manufacturing, T-shirt printing, apparel). Tailor all insights exclusively to that exact industry context. NEVER inject unrelated sector examples like Electric Vehicles (EV), Tesla, or BYD.
# # #         2. You MUST use the exact numbered Markdown headings listed below so the UI tabs can parse them correctly.
        
# # #         FORMAT YOUR RESPONSE USING THESE EXACT HEADINGS:
# # #         ## 1. Executive Summary
# # #         [Provide a high-level strategic summary customized strictly to the user's business type]

# # #         ## 2. Data Table
# # #         [Include a clean Markdown table outlining market risks, impacts, and mitigation actions relevant to the user's business]

# # #         ## 3. SWOT Analysis
# # #         [Provide a complete breakdown of Strengths, Weaknesses, Opportunities, and Threats]

# # #         ## 4. Strategic Recommendations
# # #         [Provide actionable, step-by-step guidance, timelines, and implementation metrics]
# # #         """
    
# # #     response = smart_llm.invoke(prompt)
# # #     return {"report": response.content, "messages": ["Generator: Response produced."]}

# # # def critic_agent(state: AgentState):
# # #     report = state["report"]
# # #     query = state["messages"][0]
# # #     intent = classify_intent(query)
    
# # #     # Informational summaries pass automatically if valid output exists
# # #     if intent == "INFORMATIONAL_SUMMARY":
# # #         is_approved = len(report.strip()) > 50 and "Error:" not in report
# # #         return {
# # #             "is_approved": is_approved,
# # #             "revision_count": state.get("revision_count", 0) + 1,
# # #             "messages": [f"Critic: Informational Check={'Passed' if is_approved else 'FAILED'}"]
# # #         }
    
# # #     # Financial and Business Reports Quality Gate
# # #     query_keywords = [word.lower() for word in query.split() if len(word) > 3]
# # #     relevance_pass = any(key in report.lower() for key in query_keywords)
# # #     forbidden_fallback = "wipro" in report.lower() and "wipro" not in query.lower()
    
# # #     is_approved = relevance_pass and not forbidden_fallback and "Error:" not in report
# # #     if intent == "FINANCIAL_ANALYSIS":
# # #         is_approved = is_approved and "|" in report  # Must have a Markdown table

# # #     return {
# # #         "is_approved": is_approved,
# # #         "revision_count": state.get("revision_count", 0) + 1,
# # #         "messages": [f"Critic: Quality Gate Check={'Passed' if is_approved else 'FAILED'}"]
# # #     }

# # import os
# # import json
# # import time
# # from pathlib import Path
# # from langchain_groq import ChatGroq
# # from state import AgentState
# # import yfinance as yf
# # import tempfile

# # # --- INTEGRATION: Gaurav's RAG & Scraper Modules ---
# # from rag.rag_pipeline import RAGPipeline
# # from rag.utils.data_loader import build_dataset  
# # from rag.retriever import has_query_evidence    

# # # --- CONFIGURATION ---
# # smart_llm = ChatGroq(
# #     model="openai/gpt-oss-120b", 
# #     temperature=0.3,
# #     groq_api_key=os.getenv("GROQ_API_KEY")
# # )

# # # Use system temp directory cache to prevent workspace file-watchers from auto-reloading
# # TEMP_CACHE_DIR = os.path.join(tempfile.gettempdir(), "omnisight_rag_cache")
# # if not os.path.exists(TEMP_CACHE_DIR):
# #     os.makedirs(TEMP_CACHE_DIR)
# # DATA_FILE = Path(TEMP_CACHE_DIR) / "market_data.json"

# # rag_system = RAGPipeline()

# # # --- HELPER FUNCTIONS ---

# # def classify_intent(query: str) -> str:
# #     """Classifies incoming query to prevent forcing business reports on general requests."""
# #     query_lower = query.lower()
    
# #     # STRICT Financial Check: Only trigger if looking up an actual public stock symbol or explicit ticker terms
# #     if any(k in query_lower for k in ["stock price", "ticker", "market cap", "pe ratio", "nse:", "bse:"]):
# #         return "FINANCIAL_ANALYSIS"
        
# #     # Full Strategic / Business Report Intent
# #     if any(k in query_lower for k in ["swot", "business plan", "competitor analysis", "strategic recommendation", "market research", "executive summary", "revenue", "sales", "printing", "business"]):
# #         return "BUSINESS_REPORT"
        
# #     # File Summaries, Resumes, or General Questions
# #     return "INFORMATIONAL_SUMMARY"

# # def get_financial_metrics(query: str):
# #     """
# #     Architect Tool: Smart Ticker Discovery for Global and Indian Markets.
# #     """
# #     try:
# #         print(f"--- Architect: Discovering ticker for '{query}'... ---")
# #         search_term = " ".join(query.split()[:2])
# #         search = yf.Search(search_term, max_results=3)
        
# #         if not search.quotes:
# #             return "Financial data: No public ticker discovered for this entity."
            
# #         quotes = search.quotes
# #         best_quote = quotes[0]
# #         for q in quotes:
# #             if any(exch in q.get('exchange', '') for exch in ['NMS', 'NYQ', 'NGM']): # US Tech Exchanges
# #                 best_quote = q
# #                 break
        
# #         ticker = best_quote['symbol']
# #         stock = yf.Ticker(ticker)
# #         info = stock.info
        
# #         metrics = {
# #             "Entity Name": info.get("longName", "N/A"),
# #             "Ticker": ticker,
# #             "Exchange": info.get("exchange", "N/A"),
# #             "Market Cap": info.get("marketCap", "N/A"),
# #             "Total Revenue": info.get("totalRevenue", "N/A"),
# #             "Trailing P/E": info.get("trailingPE", "N/A"),
# #             "Debt to Equity": info.get("debtToEquity", "N/A"),
# #             "Current Price": f"{info.get('currentPrice', 'N/A')} {info.get('currency', 'USD')}",
# #             "52 Week High": info.get("fiftyTwoWeekHigh", "N/A")
# #         }
# #         return metrics
# #     except Exception as e:
# #         return f"Financial data retrieval failed: {str(e)}"

# # # --- AGENT NODES ---

# # def planner_agent(state: AgentState):
# #     query = state['messages'][-1]
# #     print(f"\n[PLANNER]: Analyzing query intent for: {query[:60]}...")
# #     return {
# #         "plan": f"Execute targeted research for: {query}",
# #         "messages": ["Planner: Task categorized. Initiating research."]
# #     }

# # def researcher_agent(state: AgentState):
# #     """
# #     Architect Role: Live Search & Context Integrator.
# #     Clears stale context if the query shifts industry or topic.
# #     """
# #     query = state['messages'][0]
# #     intent = classify_intent(query)
# #     needs_update = True

# #     # 1. Stale Context Prevention: Clear local cache if query changes topic
# #     if DATA_FILE.exists():
# #         with open(DATA_FILE, "r", encoding="utf-8") as f:
# #             local_content = f.read().lower()
        
# #         query_terms = [w.lower() for w in query.split() if len(w) > 3]
# #         term_match = any(term in local_content for term in query_terms)

# #         if not term_match or not has_query_evidence(query, local_content):
# #             print(f"--- Architect: Topic shift or stale data detected. Clearing cache... ---")
# #             try:
# #                 os.remove(DATA_FILE)
# #             except Exception as e:
# #                 print(f"--- Architect: Warning: Could not delete stale file: {e} ---")
# #         else:
# #             print(f"--- Architect: Relevant local context found. ---")
# #             needs_update = False

# #     if needs_update:
# #         print(f"--- Architect: Triggering LIVE SCRAPE for '{query[:40]}'... ---")
# #         build_dataset(query=query)
# #         rag_system.initialize(str(DATA_FILE))
# #     else:
# #         if not rag_system._initialized:
# #             rag_system.initialize(str(DATA_FILE))

# #     # 2. Financial API Execution (only for financial queries)
# #     fin_data = get_financial_metrics(query) if intent == "FINANCIAL_ANALYSIS" else "N/A (Not a financial query)"

# #     # 3. RAG Retrieval
# #     rag_response = rag_system.generate_response(query)
    
# #     combined_context = f"REAL-TIME FINANCIAL METRICS:\n{json.dumps(fin_data, indent=2) if isinstance(fin_data, dict) else fin_data}\n\nRETRIEVED CONTEXT & DOCUMENTS:\n{rag_response}"
    
# #     return {
# #         "research_data": combined_context, 
# #         "messages": ["Researcher: Context retrieved."]
# #     }

# # def report_generator_agent(state: AgentState):
# #     research = state["research_data"]
# #     query = state['messages'][0]
# #     intent = classify_intent(query)
    
# #     # -------------------------------------------------------------
# #     # ROUTE 1: Informational Query / Document Summary / Resume Overview
# #     # -------------------------------------------------------------
# #     if intent == "INFORMATIONAL_SUMMARY":
# #         prompt = f"""
# #         You are a helpful and precise AI Assistant.
        
# #         USER REQUEST: {query}
        
# #         PROVIDED CONTEXT / ATTACHED FILE:
# #         {research}
        
# #         STRICT INSTRUCTIONS:
# #         1. Direct Answer: Answer the user's specific query clearly and directly based strictly on the provided context.
# #         2. DO NOT format this as a business strategy, corporate hiring recommendation, investor proposal, or SWOT report.
# #         3. Do NOT invent external metrics, financial budgets, or market forecasts.
# #         4. Use clean Markdown formatting (bullet points and bold subheadings).
# #         """
        
# #     # -------------------------------------------------------------
# #     # ROUTE 2: Financial & Valuation Analysis
# #     # -------------------------------------------------------------
# #     elif intent == "FINANCIAL_ANALYSIS":
# #         prompt = f"""
# #         You are a Senior Equity Research Analyst.
# #         USER REQUEST: {query}
        
# #         RESEARCH DATA:
# #         {research}
        
# #         FORMAT YOUR RESPONSE AS:
# #         1. Financial & Valuation Overview
# #         2. Key Metrics Comparison Table
# #         3. Market Risk & Investment Conclusion
# #         """
        
# #     # -------------------------------------------------------------
# #     # ROUTE 3: Explicit Strategic / Business Decision Request
# #     # -------------------------------------------------------------
# #     else:
# #         prompt = f"""
# #         You are an expert Small Business and Commercial Growth Consultant.
# #         USER REQUEST: {query}
        
# #         RESEARCH DATA:
# #         {research}
        
# #         STRICT FORMATTING & CONTENT INSTRUCTIONS:
# #         1. Context Adherence: Analyze the user's specific business type mentioned in the request (e.g., retail, local manufacturing, T-shirt printing, apparel). Tailor all insights exclusively to that exact industry context. NEVER inject unrelated sector examples like Electric Vehicles (EV), Tesla, or BYD.
# #         2. You MUST use the exact numbered Markdown headings listed below so the UI tabs can parse them correctly.
        
# #         FORMAT YOUR RESPONSE USING THESE EXACT HEADINGS:
# #         ## 1. Executive Summary
# #         [Provide a high-level strategic summary customized strictly to the user's business type]

# #         ## 2. Data Table
# #         [Include a clean Markdown table outlining market risks, impacts, and mitigation actions relevant to the user's business]

# #         ## 3. SWOT Analysis
# #         [Provide a complete breakdown of Strengths, Weaknesses, Opportunities, and Threats]

# #         ## 4. Strategic Recommendations
# #         [Provide actionable, step-by-step guidance, timelines, and implementation metrics]
# #         """
    
# #     response = smart_llm.invoke(prompt)
# #     return {"report": response.content, "messages": ["Generator: Response produced."]}

# # def critic_agent(state: AgentState):
# #     report = state["report"]
# #     query = state["messages"][0]
# #     intent = classify_intent(query)
    
# #     # Informational summaries pass automatically if valid output exists
# #     if intent == "INFORMATIONAL_SUMMARY":
# #         is_approved = len(report.strip()) > 50 and "Error:" not in report
# #         return {
# #             "is_approved": is_approved,
# #             "revision_count": state.get("revision_count", 0) + 1,
# #             "messages": [f"Critic: Informational Check={'Passed' if is_approved else 'FAILED'}"]
# #         }
    
# #     # Financial and Business Reports Quality Gate
# #     query_keywords = [word.lower() for word in query.split() if len(word) > 3]
# #     relevance_pass = any(key in report.lower() for key in query_keywords)
# #     forbidden_fallback = "wipro" in report.lower() and "wipro" not in query.lower()
    
# #     is_approved = relevance_pass and not forbidden_fallback and "Error:" not in report
# #     if intent == "FINANCIAL_ANALYSIS":
# #         is_approved = is_approved and "|" in report  # Must have a Markdown table

# #     return {
# #         "is_approved": is_approved,
# #         "revision_count": state.get("revision_count", 0) + 1,
# #         "messages": [f"Critic: Quality Gate Check={'Passed' if is_approved else 'FAILED'}"]
# #     }

# import os
# import json
# import time
# from pathlib import Path
# from langchain_groq import ChatGroq
# from state import AgentState
# import yfinance as yf
# import tempfile

# # --- INTEGRATION: Gaurav's RAG & Scraper Modules ---
# from rag.rag_pipeline import RAGPipeline
# from rag.utils.data_loader import build_dataset  
# from rag.retriever import has_query_evidence    

# # --- CONFIGURATION ---
# smart_llm = ChatGroq(
#     model="openai/gpt-oss-120b", 
#     temperature=0.3,
#     groq_api_key=os.getenv("GROQ_API_KEY")
# )

# # Use system temp directory cache to prevent workspace file-watchers from auto-reloading
# TEMP_CACHE_DIR = os.path.join(tempfile.gettempdir(), "omnisight_rag_cache")
# if not os.path.exists(TEMP_CACHE_DIR):
#     os.makedirs(TEMP_CACHE_DIR)
# DATA_FILE = Path(TEMP_CACHE_DIR) / "market_data.json"

# rag_system = RAGPipeline()

# # --- HELPER FUNCTIONS ---

# def classify_intent(query: str) -> str:
#     """Classifies incoming query to prevent forcing business reports on general requests."""
#     query_lower = query.lower()
    
#     # STRICT Financial Check: Only trigger if looking up an actual public stock symbol or explicit ticker terms
#     if any(k in query_lower for k in ["stock price", "ticker", "market cap", "pe ratio", "nse:", "bse:"]):
#         return "FINANCIAL_ANALYSIS"
        
#     # Full Strategic / Business Report Intent
#     if any(k in query_lower for k in ["swot", "business plan", "competitor analysis", "strategic recommendation", "market research", "executive summary", "revenue", "sales", "printing", "business", "cookie", "brand", "start"]):
#         return "BUSINESS_REPORT"
        
#     # File Summaries, Resumes, or General Questions
#     return "INFORMATIONAL_SUMMARY"

# def get_financial_metrics(query: str):
#     """
#     Architect Tool: Smart Ticker Discovery for Global and Indian Markets.
#     """
#     try:
#         print(f"--- Architect: Discovering ticker for '{query}'... ---")
#         search_term = " ".join(query.split()[:2])
#         search = yf.Search(search_term, max_results=3)
        
#         if not search.quotes:
#             return "Financial data: No public ticker discovered for this entity."
            
#         quotes = search.quotes
#         best_quote = quotes[0]
#         for q in quotes:
#             if any(exch in q.get('exchange', '') for exch in ['NMS', 'NYQ', 'NGM']): # US Tech Exchanges
#                 best_quote = q
#                 break
        
#         ticker = best_quote['symbol']
#         stock = yf.Ticker(ticker)
#         info = stock.info
        
#         metrics = {
#             "Entity Name": info.get("longName", "N/A"),
#             "Ticker": ticker,
#             "Exchange": info.get("exchange", "N/A"),
#             "Market Cap": info.get("marketCap", "N/A"),
#             "Total Revenue": info.get("totalRevenue", "N/A"),
#             "Trailing P/E": info.get("trailingPE", "N/A"),
#             "Debt to Equity": info.get("debtToEquity", "N/A"),
#             "Current Price": f"{info.get('currentPrice', 'N/A')} {info.get('currency', 'USD')}",
#             "52 Week High": info.get("fiftyTwoWeekHigh", "N/A")
#         }
#         return metrics
#     except Exception as e:
#         return f"Financial data retrieval failed: {str(e)}"

# # --- AGENT NODES ---

# def planner_agent(state: AgentState):
#     query = state['messages'][-1]
#     print(f"\n[PLANNER]: Analyzing query intent for: {query[:60]}...")
#     return {
#         "plan": f"Execute targeted research for: {query}",
#         "messages": ["Planner: Task categorized. Initiating research."]
#     }

# # def researcher_agent(state: AgentState):
# #     """
# #     Architect Role: Live Search & Context Integrator.
# #     Clears stale context if the query shifts industry or topic.
# #     """
# #     query = state['messages'][0]
# #     intent = classify_intent(query)
# #     needs_update = True

# #     # 1. Stale Context Prevention: Clear local cache if query changes topic
# #     if DATA_FILE.exists():
# #         with open(DATA_FILE, "r", encoding="utf-8") as f:
# #             local_content = f.read().lower()
        
# #         query_terms = [w.lower() for w in query.split() if len(w) > 3]
# #         term_match = any(term in local_content for term in query_terms)

# #         if not term_match or not has_query_evidence(query, local_content):
# #             print(f"--- Architect: Topic shift or stale data detected. Clearing cache... ---")
# #             try:
# #                 os.remove(DATA_FILE)
# #             except Exception as e:
# #                 print(f"--- Architect: Warning: Could not delete stale file: {e} ---")
# #         else:
# #             print(f"--- Architect: Relevant local context found. ---")
# #             needs_update = False

# #     if needs_update:
# #         print(f"--- Architect: Triggering LIVE SCRAPE for '{query[:40]}'... ---")
# #         build_dataset(query=query)
# #         rag_system.initialize(str(DATA_FILE))
# #     else:
# #         if not rag_system._initialized:
# #             rag_system.initialize(str(DATA_FILE))

# #     # 2. Financial API Execution (only for financial queries)
# #     fin_data = get_financial_metrics(query) if intent == "FINANCIAL_ANALYSIS" else "N/A (Not a financial query)"

# #     # 3. RAG Retrieval
# #     rag_response = rag_system.generate_response(query)
    
# #     combined_context = f"REAL-TIME FINANCIAL METRICS:\n{json.dumps(fin_data, indent=2) if isinstance(fin_data, dict) else fin_data}\n\nRETRIEVED CONTEXT & DOCUMENTS:\n{rag_response}"
    
# #     return {
# #         "research_data": combined_context, 
# #         "messages": ["Researcher: Context retrieved."]
# #     }


# def researcher_agent(state: AgentState):
#     query = state['messages'][0]
#     intent = classify_intent(query)
#     needs_update = True

#     # 1. Stale Context Prevention: Force clear if query names a new entity/topic
#     if DATA_FILE.exists():
#         with open(DATA_FILE, "r", encoding="utf-8") as f:
#             local_content = f.read().lower()
        
#         # Extract significant keywords from the current query
#         query_terms = [w.lower() for w in query.split() if len(w) > 3 and w.lower() not in {"want", "scale", "company", "india", "what", "where"}]
#         term_match = any(term in local_content for term in query_terms)

#         if not term_match or not has_query_evidence(query, local_content):
#             print(f"--- Architect: Entity or topic shift detected. Clearing cache... ---")
#             try:
#                 os.remove(DATA_FILE)
#             except Exception as e:
#                 print(f"--- Architect: Warning: Could not delete stale file: {e} ---")
#         else:
#             print(f"--- Architect: Relevant local context found. ---")
#             needs_update = False

#     if needs_update:
#         print(f"--- Architect: Triggering LIVE SCRAPE for '{query[:40]}'... ---")
#         build_dataset(query=query)
#         rag_system.initialize(str(DATA_FILE))
#     else:
#         if not rag_system._initialized:
#             rag_system.initialize(str(DATA_FILE))

#     fin_data = get_financial_metrics(query) if intent == "FINANCIAL_ANALYSIS" else "N/A (Not a financial query)"
#     rag_response = rag_system.generate_response(query)
    
#     combined_context = f"REAL-TIME FINANCIAL METRICS:\n{json.dumps(fin_data, indent=2) if isinstance(fin_data, dict) else fin_data}\n\nRETRIEVED CONTEXT & DOCUMENTS:\n{rag_response}"
    
#     return {
#         "research_data": combined_context, 
#         "messages": ["Researcher: Context retrieved."]
#     }

# def report_generator_agent(state: AgentState):
#     research = state["research_data"]
#     query = state['messages'][0]
#     intent = classify_intent(query)
    
#     # -------------------------------------------------------------
#     # ROUTE 1: Informational Query / Document Summary / Resume Overview
#     # -------------------------------------------------------------
#     if intent == "INFORMATIONAL_SUMMARY":
#         prompt = f"""
#         You are a helpful and precise AI Assistant.
        
#         USER REQUEST: {query}
        
#         PROVIDED CONTEXT / ATTACHED FILE:
#         {research}
        
#         STRICT INSTRUCTIONS:
#         1. Direct Answer: Answer the user's specific query clearly and directly based strictly on the provided context.
#         2. DO NOT format this as a business strategy, corporate hiring recommendation, investor proposal, or SWOT report.
#         3. Do NOT invent external metrics, financial budgets, or market forecasts.
#         4. Use clean Markdown formatting (bullet points and bold subheadings).
#         """
        
#     # -------------------------------------------------------------
#     # ROUTE 2: Financial & Valuation Analysis
#     # -------------------------------------------------------------
#     elif intent == "FINANCIAL_ANALYSIS":
#         prompt = f"""
#         You are a Senior Equity Research Analyst.
#         USER REQUEST: {query}
        
#         RESEARCH DATA:
#         {research}
        
#         FORMAT YOUR RESPONSE AS:
#         1. Financial & Valuation Overview
#         2. Key Metrics Comparison Table
#         3. Market Risk & Investment Conclusion
#         """
        
#     # -------------------------------------------------------------
#     # ROUTE 3: Explicit Strategic / Business Decision Request
#     # -------------------------------------------------------------
#     else:
#         prompt = f"""
#         You are an expert Small Business and Commercial Growth Consultant.
#         USER REQUEST: {query}
        
#         RESEARCH DATA:
#         {research}
        
#         STRICT FORMATTING & CONTENT INSTRUCTIONS:
#         1. Context Adherence: Analyze the user's specific business type mentioned in the request (e.g., retail, cookie brand, local manufacturing, T-shirt printing). Tailor all insights exclusively to that exact industry context. Never use unrelated sector examples like Electric Vehicles, Tesla, or BYD.
#         2. MANDATORY SECTIONS: You MUST output all four sections with their exact Markdown headings so the UI tabs can parse them properly.
        
#         FORMAT YOUR RESPONSE USING THESE EXACT HEADINGS:
#         ## 1. Executive Summary
#         [Provide a high-level strategic summary customized strictly to the user's business type]

#         ## 2. Data Table
#         | Risk Category | Impact Level | Mitigation Strategy |
#         |---|---|---|
#         | [Risk 1] | [High/Med/Low] | [Action] |
#         | [Risk 2] | [High/Med/Low] | [Action] |

#         ## 3. SWOT Analysis
#         ### Strengths
#         - [Point]
#         ### Weaknesses
#         - [Point]
#         ### Opportunities
#         - [Point]
#         ### Threats
#         - [Point]

#         ## 4. Strategic Recommendations
#         [Provide actionable, step-by-step guidance, timelines, and implementation metrics]
#         """
    
#     response = smart_llm.invoke(prompt)
#     return {"report": response.content, "messages": ["Generator: Response produced."]}

# def critic_agent(state: AgentState):
#     report = state["report"]
#     query = state["messages"][0]
#     intent = classify_intent(query)
    
#     # Informational summaries pass automatically if valid output exists
#     if intent == "INFORMATIONAL_SUMMARY":
#         is_approved = len(report.strip()) > 50 and "Error:" not in report
#         return {
#             "is_approved": is_approved,
#             "revision_count": state.get("revision_count", 0) + 1,
#             "messages": [f"Critic: Informational Check={'Passed' if is_approved else 'FAILED'}"]
#         }
    
#     # Financial and Business Reports Quality Gate
#     query_keywords = [word.lower() for word in query.split() if len(word) > 3]
#     relevance_pass = any(key in report.lower() for key in query_keywords)
#     forbidden_fallback = "wipro" in report.lower() and "wipro" not in query.lower()
    
#     is_approved = relevance_pass and not forbidden_fallback and "Error:" not in report
#     if intent == "FINANCIAL_ANALYSIS":
#         is_approved = is_approved and "|" in report  # Must have a Markdown table

#     return {
#         "is_approved": is_approved,
#         "revision_count": state.get("revision_count", 0) + 1,
#         "messages": [f"Critic: Quality Gate Check={'Passed' if is_approved else 'FAILED'}"]
#     }


import os
import json
import time
from pathlib import Path
from langchain_groq import ChatGroq
from state import AgentState
import yfinance as yf

# --- INTEGRATION: Gaurav's RAG & Scraper Modules ---
from rag.rag_pipeline import RAGPipeline
from rag.utils.data_loader import build_dataset  
from rag.retriever import has_query_evidence    

# --- CONFIGURATION ---
smart_llm = ChatGroq(
    model="openai/gpt-oss-120b", 
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Hardcoded permanent absolute path for market_data.json as requested
DATA_FILE = Path(r"C:\Users\ASUS\OneDrive\Attachments\Desktop\Finaly yr prjct\rag\data\market_data.json")

# Ensure the directory exists
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

rag_system = RAGPipeline()

# --- HELPER FUNCTIONS ---

def classify_intent(query: str) -> str:
    """Classifies incoming query to ensure strategic business requests trigger full report routes."""
    query_lower = query.lower()
    
    # STRICT Financial Check: Only trigger if looking up an actual public stock symbol or explicit ticker terms
    if any(k in query_lower for k in ["stock price", "ticker", "market cap", "pe ratio", "nse:", "bse:"]):
        return "FINANCIAL_ANALYSIS"
        
    # Full Strategic / Business Report Intent (Includes expansion, scale, office, cities)
    if any(k in query_lower for k in ["swot", "business plan", "competitor analysis", "strategic recommendation", "market research", "executive summary", "revenue", "sales", "printing", "business", "cookie", "brand", "start", "scale", "expand", "office", "cities", "state"]):
        return "BUSINESS_REPORT"
        
    # File Summaries, Resumes, or General Questions
    return "INFORMATIONAL_SUMMARY"

def get_financial_metrics(query: str):
    """
    Architect Tool: Smart Ticker Discovery for Global and Indian Markets.
    """
    try:
        print(f"--- Architect: Discovering ticker for '{query}'... ---")
        search_term = " ".join(query.split()[:2])
        search = yf.Search(search_term, max_results=3)
        
        if not search.quotes:
            return "Financial data: No public ticker discovered for this entity."
            
        quotes = search.quotes
        best_quote = quotes[0]
        for q in quotes:
            if any(exch in q.get('exchange', '') for exch in ['NMS', 'NYQ', 'NGM']): # US Tech Exchanges
                best_quote = q
                break
        
        ticker = best_quote['symbol']
        stock = yf.Ticker(ticker)
        info = stock.info
        
        metrics = {
            "Entity Name": info.get("longName", "N/A"),
            "Ticker": ticker,
            "Exchange": info.get("exchange", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "Total Revenue": info.get("totalRevenue", "N/A"),
            "Trailing P/E": info.get("trailingPE", "N/A"),
            "Debt to Equity": info.get("debtToEquity", "N/A"),
            "Current Price": f"{info.get('currentPrice', 'N/A')} {info.get('currency', 'USD')}",
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A")
        }
        return metrics
    except Exception as e:
        return f"Financial data retrieval failed: {str(e)}"

# --- AGENT NODES ---

def planner_agent(state: AgentState):
    query = state['messages'][-1]
    print(f"\n[PLANNER]: Analyzing query intent for: {query[:60]}...")
    return {
        "plan": f"Execute targeted research for: {query}",
        "messages": ["Planner: Task categorized. Initiating research."]
    }

def researcher_agent(state: AgentState):
    """
    Architect Role: Live Search & Context Integrator.
    Clears stale context if the query shifts industry or topic.
    """
    query = state['messages'][0]
    intent = classify_intent(query)
    needs_update = True

    # 1. Stale Context Prevention: Clear local cache if query changes topic
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            local_content = f.read().lower()
        
        query_terms = [w.lower() for w in query.split() if len(w) > 3 and w.lower() not in {"want", "scale", "company", "india", "what", "where"}]
        term_match = any(term in local_content for term in query_terms)

        if not term_match or not has_query_evidence(query, local_content):
            print(f"--- Architect: Topic shift or stale data detected. Clearing cache... ---")
            try:
                os.remove(DATA_FILE)
            except Exception as e:
                print(f"--- Architect: Warning: Could not delete stale file: {e} ---")
        else:
            print(f"--- Architect: Relevant local context found. ---")
            needs_update = False

    if needs_update:
        print(f"--- Architect: Triggering LIVE SCRAPE for '{query[:40]}'... ---")
        build_dataset(query=query)
        rag_system.initialize(str(DATA_FILE))
    else:
        if not rag_system._initialized:
            rag_system.initialize(str(DATA_FILE))

    # 2. Financial API Execution (only for financial queries)
    fin_data = get_financial_metrics(query) if intent == "FINANCIAL_ANALYSIS" else "N/A (Not a financial query)"

    # 3. RAG Retrieval
    rag_response = rag_system.generate_response(query)
    
    combined_context = f"REAL-TIME FINANCIAL METRICS:\n{json.dumps(fin_data, indent=2) if isinstance(fin_data, dict) else fin_data}\n\nRETRIEVED CONTEXT & DOCUMENTS:\n{rag_response}"
    
    return {
        "research_data": combined_context, 
        "messages": ["Researcher: Context retrieved."]
    }

def report_generator_agent(state: AgentState):
    research = state["research_data"]
    query = state['messages'][0]
    intent = classify_intent(query)
    
    # -------------------------------------------------------------
    # ROUTE 1: Informational Query / Document Summary / Resume Overview
    # -------------------------------------------------------------
    if intent == "INFORMATIONAL_SUMMARY":
        prompt = f"""
        You are a helpful and precise AI Assistant.
        
        USER REQUEST: {query}
        
        PROVIDED CONTEXT / ATTACHED FILE:
        {research}
        
        STRICT INSTRUCTIONS:
        1. Direct Answer: Answer the user's specific query clearly and directly based strictly on the provided context.
        2. DO NOT format this as a business strategy, corporate hiring recommendation, investor proposal, or SWOT report.
        3. Do NOT invent external metrics, financial budgets, or market forecasts.
        4. Use clean Markdown formatting (bullet points and bold subheadings).
        """
        
    # -------------------------------------------------------------
    # ROUTE 2: Financial & Valuation Analysis
    # -------------------------------------------------------------
    elif intent == "FINANCIAL_ANALYSIS":
        prompt = f"""
        You are a Senior Equity Research Analyst.
        USER REQUEST: {query}
        
        RESEARCH DATA:
        {research}
        
        FORMAT YOUR RESPONSE AS:
        1. Financial & Valuation Overview
        2. Key Metrics Comparison Table
        3. Market Risk & Investment Conclusion
        """
        
    # -------------------------------------------------------------
    # ROUTE 3: Explicit Strategic / Business / Expansion Request
    # -------------------------------------------------------------
    else:
        prompt = f"""
        You are an expert Corporate Growth and Expansion Consultant.
        USER REQUEST: {query}
        
        RESEARCH DATA:
        {research}
        
        STRICT FORMATTING & CONTENT INSTRUCTIONS:
        1. Context Adherence: Tailor all insights exclusively to the user's specific scenario (e.g., corporate expansion, IT sector scaling, regional office setup in India, retail, manufacturing). Never use unrelated sector examples like Electric Vehicles, Tesla, or BYD.
        2. MANDATORY SECTIONS: You MUST output all four sections with their exact Markdown headings so the UI tabs can parse them properly.
        
        FORMAT YOUR RESPONSE USING THESE EXACT HEADINGS:
        ## 1. Executive Summary
        [Provide a high-level strategic summary customized strictly to the user's expansion or business request]

        ## 2. Data Table
        | Expansion City / Sector / Risk | Infrastructure Readiness | Key Risk / Challenge | Mitigation Strategy |
        |---|---|---|---|
        | [Item Name 1] | [High/Med] | [e.g., Talent retention / Real estate cost] | [Action] |
        | [Item Name 2] | [High/Med] | [e.g., Infrastructure lag] | [Action] |

        ## 3. SWOT Analysis
        ### Strengths
        - [Point]
        ### Weaknesses
        - [Point]
        ### Opportunities
        - [Point]
        ### Threats
        - [Point]

        ## 4. Strategic Recommendations
        [Provide actionable, step-by-step guidance, timelines, and implementation metrics]
        """
    
    response = smart_llm.invoke(prompt)
    return {"report": response.content, "messages": ["Generator: Response produced."]}

def critic_agent(state: AgentState):
    report = state["report"]
    query = state["messages"][0]
    intent = classify_intent(query)
    
    # Informational summaries pass automatically if valid output exists
    if intent == "INFORMATIONAL_SUMMARY":
        is_approved = len(report.strip()) > 50 and "Error:" not in report
        return {
            "is_approved": is_approved,
            "revision_count": state.get("revision_count", 0) + 1,
            "messages": [f"Critic: Informational Check={'Passed' if is_approved else 'FAILED'}"]
        }
    
    # Financial and Business Reports Quality Gate
    query_keywords = [word.lower() for word in query.split() if len(word) > 3]
    relevance_pass = any(key in report.lower() for key in query_keywords)
    forbidden_fallback = "wipro" in report.lower() and "wipro" not in query.lower()
    
    is_approved = relevance_pass and not forbidden_fallback and "Error:" not in report
    if intent == "FINANCIAL_ANALYSIS":
        is_approved = is_approved and "|" in report  # Must have a Markdown table

    return {
        "is_approved": is_approved,
        "revision_count": state.get("revision_count", 0) + 1,
        "messages": [f"Critic: Quality Gate Check={'Passed' if is_approved else 'FAILED'}"]
    }