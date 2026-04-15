import os
import time
from google import genai
from rag.retriever import Retriever
from dotenv import load_dotenv
from rag.planner_agent import PlannerAgent
from utils.scraper import collect_market_data

load_dotenv()

MIN_STRONG_CONTEXT_SCORE = 0.60
MIN_DYNAMIC_CONTEXT_SCORE = 0.40
MIN_OFFICIAL_CONTEXT_SCORE = 0.40
MAX_DYNAMIC_ARTICLES = 8

OFFICIAL_FINANCE_SOURCES = {
    "rbi",
    "sebi",
    "ministry_of_finance",
    "data_gov",
}


class RAGPipeline:

    def __init__(self):
        self.retriever = Retriever()
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.planner = PlannerAgent()
        self._initialized = False
        self._documents = []

    def initialize(self, file_path):
        docs = self.retriever.load_documents(file_path)
        self.retriever.build_index(docs)
        self._documents = docs
        self._initialized = True

    # ---------------- RETRIEVE ----------------

    def _retrieve_context(self, sub_queries, k=6):
        all_context = []

        for q in sub_queries:
            results = self.retriever.retrieve(q, k=k)
            all_context.extend(results)

        # remove duplicates
        seen = set()
        context = []

        for item in all_context:
            if item["text"] not in seen:
                context.append(item)
                seen.add(item["text"])

        return context

    # ---------------- FILTER ----------------

    def _filter_context(self, context, domain, allow_dynamic_relaxed=False):
        filtered = []

        for item in context:
            score = item.get("relevance_score", 0)
            meta = item["metadata"]

            item_domain = meta.get("domain")
            source = meta.get("source")

            # domain boost
            if item_domain == domain:
                score += 0.15

            if score >= MIN_STRONG_CONTEXT_SCORE:
                filtered.append(item)

            elif allow_dynamic_relaxed and score >= MIN_DYNAMIC_CONTEXT_SCORE:
                filtered.append(item)

            elif (
                allow_dynamic_relaxed
                and source in OFFICIAL_FINANCE_SOURCES
                and score >= MIN_OFFICIAL_CONTEXT_SCORE
            ):
                filtered.append(item)

        return filtered

    # ---------------- FORMAT ----------------

    def _format_context(self, context):
        context_text = ""

        for item in context:
            meta = item.get("metadata", {})

            source = meta.get("source", "unknown")
            credibility = meta.get("credibility", 0.5)
            relevance = item.get("relevance_score", 0)

            context_text += f"""
[Source: {source} | Credibility: {credibility} | Relevance: {relevance:.2f}]
{item['text']}
"""

        return context_text

    # ---------------- DYNAMIC UPDATE ----------------

    def _refresh_from_query(self, query):
        print("\n===== DYNAMIC SCRAPE =====")

        fresh_data = collect_market_data(
            query=query,
            max_articles=MAX_DYNAMIC_ARTICLES,
            sleep_seconds=0.25,
        )

        print(f"Dynamic articles collected: {len(fresh_data)}")

        if not fresh_data:
            return False

        fresh_docs = self.retriever.documents_from_items(fresh_data)

        if not fresh_docs:
            return False

        seen = {doc["text"] for doc in self._documents}
        new_docs = [doc for doc in fresh_docs if doc["text"] not in seen]

        if not new_docs:
            return False

        self._documents.extend(new_docs)

        # incremental indexing
        self.retriever.vector_store.add_embeddings(
            self.retriever.embedder.encode([d["text"] for d in new_docs]),
            [d["text"] for d in new_docs],
            [d for d in new_docs]
        )

        return True

    # ---------------- MAIN ----------------

    def generate_response(self, query):

        if not self._initialized:
            raise RuntimeError("Initialize RAG first")

        # STEP 1: PLAN
        plan = self.planner.plan(query)
        domain = plan["domain"]
        sub_queries = plan["sub_queries"]

        # STEP 2: RETRIEVE
        context = self._retrieve_context(sub_queries)

        if not context:
            if self._refresh_from_query(query):
                context = self._retrieve_context(sub_queries)

        if not context:
            return {"answer": "No relevant data found.", "context": []}

        # STEP 3: FILTER
        relevant_context = self._filter_context(context, domain)

        if not relevant_context:
            if self._refresh_from_query(query):
                context = self._retrieve_context(sub_queries)
                relevant_context = self._filter_context(
                    context, domain, allow_dynamic_relaxed=True
                )

        if not relevant_context:
            return {
                "answer": "Insufficient data",
                "context": context
            }

        # STEP 4: FORMAT
        context_text = self._format_context(relevant_context)

        # STEP 5: PROMPT
        prompt = f"""
You are an expert Business Intelligence Analyst.

Detected Domain: {domain}

Your task is to analyze the query using ONLY the provided context.

--------------------- RULES ---------------------

- Use ONLY the given context. Do NOT use outside knowledge.
- Focus ONLY on information relevant to the query.
- Prefer high-credibility sources.
- Extract real company names, products, or entities if present.
- If partial information is available → still provide useful insights.
- Avoid generic or vague statements.
- If data is truly insufficient → clearly say "Insufficient data".

--------------------- CONTEXT ---------------------

{context_text}

--------------------- QUERY ---------------------

{query}

--------------------- OUTPUT FORMAT ---------------------

1. Key Entities
   - List all relevant companies / competitors / products mentioned.

2. Key Insights
   - Bullet points with concrete findings from the data.

3. Detailed Analysis
   - Explain competition, strategies, or trends based on context.

4. Risks / Challenges
   - Identify possible risks or limitations from the data.

5. Strategic Recommendations
   - Give actionable suggestions ONLY if supported by context.

6. Conclusion
   - Short summary of findings.

7. Sources Used
   - List sources in format: [source | credibility]

--------------------- IMPORTANT ---------------------

- DO NOT hallucinate.
- DO NOT assume missing data.
- DO NOT give textbook definitions.
- Be specific, data-driven, and concise.
"""

        # STEP 6: LLM
        for _ in range(3):
            try:
                response = self.client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                    contents=prompt
                )

                return {
                    "answer": response.text,
                    "context": relevant_context
                }

            except Exception:
                time.sleep(2)

        return {
            "answer": "Model unavailable",
            "context": relevant_context
        }