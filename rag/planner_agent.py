import json
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

class PlannerAgent:
    def __init__(self):
        # Initializing Groq instead of Gemini
        self.llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0.2, # Lower temperature for consistent JSON structure
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def detect_domain(self, query):
        q = query.lower()
        if "smartphone" in q or "mobile" in q:
            return "smartphone"
        if "electric vehicle" in q or "ev" in q:
            return "ev"
        if "bank" in q or "finance" in q:
            return "finance"
        if "startup" in q:
            return "startup"
        if "chemical" in q or "tata" in q: # Added for your specific Tata project
            return "industrial"
        return "general"

    def generate_subqueries(self, query, domain):
        # ... [Logic remains the same as your provided code for fallback]
        query_lower = query.lower()
        base = [query]
        if any(word in query_lower for word in ["compare", "comparison", "vs", "versus"]):
            base += [f"{query} differences", f"{query} features pricing comparison"]
        else:
            base += [f"{query} key facts", f"{query} analysis"]
        return base

    def _fallback_plan(self, query):
        domain = self.detect_domain(query)
        sub_queries = self.generate_subqueries(query, domain)
        return {
            "domain": domain,
            "sub_queries": sub_queries,
            "response_style": "answer the user's exact question using only retrieved context",
        }

    def _normalize_plan(self, query, plan_data):
        # ... [Logic remains the same as your provided code]
        domain = str(plan_data.get("domain", "")).strip().lower() or self.detect_domain(query)
        raw_sub_queries = plan_data.get("sub_queries", [])
        sub_queries = []
        if isinstance(raw_sub_queries, list):
            for item in raw_sub_queries:
                value = str(item).strip()
                if value and value not in sub_queries:
                    sub_queries.append(value)
        if query not in sub_queries:
            sub_queries.insert(0, query)
        return {
            "domain": domain,
            "sub_queries": sub_queries[:6],
            "response_style": str(plan_data.get("response_style", "concise factual answer")).strip(),
        }

    def _extract_json(self, text):
        # Cleans LLM output to ensure we only get the JSON block
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return text[start:end + 1]
        return text

    def _llm_plan(self, query):
        system_prompt = "You are a query planning agent for a RAG system. Return ONLY valid JSON."
        user_prompt = f"""
User query: {query}

Return JSON schema:
{{
  "domain": "short domain label",
  "response_style": "e.g., comparison table, factual summary",
  "sub_queries": ["original query", "3-5 search-optimized queries"]
}}
"""
        # Groq Call
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        json_text = self._extract_json(response.content)
        plan_data = json.loads(json_text)
        return self._normalize_plan(query, plan_data)

    def plan(self, query):
        for attempt in range(2):
            try:
                return self._llm_plan(query)
            except Exception as exc:
                print(f"Planner retry {attempt + 1} failed: {exc}")
                time.sleep(1)
        return self._fallback_plan(query)