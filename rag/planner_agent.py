# rag/planner_agent.py

import json
import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()


class PlannerAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = os.getenv(
            "GEMINI_PLANNER_MODEL",
            os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        )

    def detect_domain(self, query):
        q = query.lower()

        if "smartphone" in q or "mobile" in q:
            return "smartphone"
        if "electric vehicle" in q or "ev" in q:
            return "ev"
        if any(word in q for word in [
            "bank", "finance", "financial", "stock", "stocks", "share",
            "shares", "equity", "sebi", "rbi", "investment", "investor",
            "nifty", "sensex", "mutual fund", "nbfc"
        ]):
            return "finance"
        if "startup" in q:
            return "startup"
        return "general"

    def generate_subqueries(self, query, domain):
        query_lower = query.lower()
        base = [query]

        if any(word in query_lower for word in ["compare", "comparison", "vs", "versus"]):
            base += [
                f"{query} differences",
                f"{query} features pricing comparison",
                f"{query} market share",
                f"{query} strengths weaknesses",
            ]
        elif any(word in query_lower for word in ["competitor", "competitors", "rival", "rivals", "players"]):
            base += [
                f"{query} top competitors",
                f"{query} market share",
                f"{query} rival companies",
                f"{query} competitive landscape",
            ]
        elif any(word in query_lower for word in ["strength", "weakness", "swot"]):
            base += [
                f"{query} SWOT analysis",
                f"{query} strengths weaknesses opportunities threats",
                f"{query} market position",
                f"{query} competitor strategy",
            ]
        elif any(word in query_lower for word in ["strategy", "strategic", "move", "launch", "partnership", "acquisition", "investment"]):
            base += [
                f"{query} recent strategic moves",
                f"{query} partnerships launches acquisitions investments",
                f"{query} competitor strategy",
                f"{query} latest developments",
            ]
        elif any(word in query_lower for word in ["feature", "features", "pricing", "price"]):
            base += [
                f"{query} features",
                f"{query} pricing",
                f"{query} specifications",
                f"{query} competitor comparison",
            ]
        elif any(word in query_lower for word in ["risk", "threat", "challenge"]):
            base += [
                f"{query} causes",
                f"{query} impact",
                f"{query} mitigation",
            ]
        elif any(word in query_lower for word in ["trend", "outlook", "forecast", "future"]):
            base += [
                f"{query} latest developments",
                f"{query} growth drivers",
                f"{query} market outlook",
            ]
        elif any(word in query_lower for word in ["what", "why", "how", "explain", "overview"]):
            base += [
                f"{query} explanation",
                f"{query} key facts",
                f"{query} summary",
            ]
        else:
            base += [
                f"{query} key facts",
                f"{query} analysis",
                f"{query} latest information",
            ]

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

        if not sub_queries:
            sub_queries = self.generate_subqueries(query, domain)

        return {
            "domain": domain,
            "sub_queries": sub_queries[:6],
            "response_style": str(
                plan_data.get("response_style", "answer the user's exact question using only retrieved context")
            ).strip(),
        }

    def _extract_json(self, text):
        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 3:
                text = "\n".join(lines[1:-1]).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]

        return text

    def _llm_plan(self, query):
        prompt = f"""
You are a query planning agent for a RAG system.

User query:
{query}

Return ONLY valid JSON with this exact schema:
{{
  "domain": "one short domain label",
  "response_style": "how the final answer should be shaped",
  "sub_queries": [
    "the original user query",
    "3 to 5 retrieval-focused search queries"
  ]
}}

Rules:
- Keep the domain short and lowercase.
- Infer the user's real intent from the query.
- Make sub_queries fit the query intent, not a fixed business template.
- Keep all sub_queries specific and useful for retrieval.
- Make response_style short and practical, for example:
  "concise factual answer", "comparison table", "step-by-step explanation", "market analysis summary"
- Do not include markdown, comments, or explanation.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        response_text = getattr(response, "text", "") or ""
        json_text = self._extract_json(response_text)
        plan_data = json.loads(json_text)
        return self._normalize_plan(query, plan_data)

    def plan(self, query):
        for attempt in range(2):
            try:
                return self._llm_plan(query)
            except Exception as exc:
                print(f"Planner retry {attempt + 1} failed:", exc)
                time.sleep(1)

        return self._fallback_plan(query)
