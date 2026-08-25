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
    model="llama-3.3-70b-versatile", 
    temperature=0.5,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

DATA_FILE = Path(__file__).resolve().parent / "rag" / "data" / "market_data.json"
rag_system = RAGPipeline()

# --- FINANCIAL TOOLS ---

def get_financial_metrics(query):
    """
    Architect Tool: Smart Ticker Discovery for Global and Indian Markets.
    """
    try:
        print(f"--- Architect: Discovering ticker for '{query}'... ---")
        # Extract potential company name (first two words usually)
        search_term = " ".join(query.split()[:2])
        search = yf.Search(search_term, max_results=3)
        
        if not search.quotes:
            return "Financial data: No public ticker discovered for this entity."
            
        # Priority Logic: Prefer NASDAQ/NYSE for global tech, then NSE/BSE
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
    print(f"\n[PLANNER]: Analyzing query intent for: {query}")
    return {
        "plan": f"Execute deep-dive research for {query}",
        "messages": ["Planner: Task categorized. Initiating global-ready research."]
    }

def researcher_agent(state: AgentState):
    """
    Architect Role: Live Search & Financial Integrator.
    Clears stale context if the company has changed.
    """
    query = state['messages'][0]
    needs_update = True

    # 1. Stale Context Prevention: If local data doesn't mention the query, wipe it.
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            local_content = f.read()
        
        # Now that the file is closed, we can delete it safely on Windows
        if not has_query_evidence(query, local_content):
            print(f"--- Architect: Stale data detected. Clearing cache for '{query}'... ---")
            try:
                os.remove(DATA_FILE)
            except Exception as e:
                print(f"--- Architect: Warning: Could not delete stale file: {e} ---")
        else:
            print(f"--- Architect: Relevant local context found. ---")
            needs_update = False

    if needs_update:
        print(f"--- Architect: Triggering LIVE SCRAPE for '{query}'... ---")
        build_dataset(query=query)
        rag_system.initialize(str(DATA_FILE))
    else:
        if not rag_system._initialized:
            rag_system.initialize(str(DATA_FILE))

    # 2. Financial API Execution (Smart Discovery)
    fin_data = get_financial_metrics(query)

    # 3. RAG Retrieval
    rag_response = rag_system.generate_response(query)
    
    combined_context = f"REAL-TIME FINANCIAL METRICS:\n{json.dumps(fin_data, indent=2)}\n\nMARKET NEWS & RESEARCH:\n{rag_response}"
    
    return {
        "research_data": combined_context, 
        "messages": ["Researcher: Unified global data retrieved."]
    }

def report_generator_agent(state: AgentState):
    research = state["research_data"]
    query = state['messages'][0].lower() 
    
    if any(word in query for word in ["stock", "valuation", "market cap", "revenue", "compare"]):
        persona = "Senior Equity Research Analyst"
        instruction = "Create a FINANCIAL & CAPITAL ANALYSIS with a clean Markdown comparison table."
    else:
        persona = "Strategic Business Consultant"
        instruction = "Create a professional SWOT analysis for strategic decision-making."

    prompt = f"""
    You are a {persona}. 
    Target Query: {query}

    {instruction}
    
    RESEARCH DATA:
    {research}
    
    FORMAT:
    1. Executive Summary (MUST address the specific companies in the query)
    2. Data Table (Use the metrics from research)
    3. SWOT Analysis or Competitive Deep-dive
    4. Strategic Recommendation for decision-making
    """
    
    response = smart_llm.invoke(prompt)
    return {"report": response.content, "messages": [f"Generator: {persona} report produced."]}

def critic_agent(state: AgentState):
    report = state["report"]
    query = state["messages"][0].lower()
    
    # --- ARCHITECT QUALITY GATE: RELEVANCE CHECK ---
    # Extract the main company name from the query (e.g., 'apple')
    query_keywords = [word for word in query.split() if len(word) > 3]
    
    # The report fails if it doesn't mention the companies requested
    relevance_pass = any(key in report.lower() for key in query_keywords)
    
    # The report fails if it falls back to 'Wipro' when asking for 'Apple'
    forbidden_fallback = "wipro" in report.lower() and "wipro" not in query
    
    is_approved = relevance_pass and not forbidden_fallback and "Error:" not in report
    
    if "stock" in query or "market cap" in query:
        is_approved = is_approved and "|" in report # Must have a table

    return {
        "is_approved": is_approved,
        "revision_count": state.get("revision_count", 0) + 1,
        "messages": [f"Critic: Relevance Check={'Passed' if is_approved else 'FAILED'}"]
    }