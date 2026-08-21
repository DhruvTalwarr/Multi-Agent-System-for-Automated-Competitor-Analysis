import os
import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from rag.retriever import Retriever
from rag.retriever import has_query_evidence
from dotenv import load_dotenv
from rag.planner_agent import PlannerAgent
from rag.utils.scraper import collect_market_data

load_dotenv()

MIN_STRONG_CONTEXT_SCORE = 0.60
MIN_DYNAMIC_CONTEXT_SCORE = 0.40
MAX_DYNAMIC_ARTICLES = 8

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        # Initialize Groq via LangChain
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0.5,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.planner = PlannerAgent()
        self._initialized = False
        self._documents = []

    def initialize(self, file_path):
        docs = self.retriever.load_documents(file_path)
        self.retriever.build_index(docs)
        self._documents = docs
        self._initialized = True

    def _retrieve_context(self, sub_queries, k=6):
        all_context = []
        for q in sub_queries:
            results = self.retriever.retrieve(q, k=k)
            all_context.extend(results)

        seen = set()
        context = []
        for item in all_context:
            if item["text"] not in seen:
                context.append(item)
                seen.add(item["text"])
        return context

    def _filter_context(self, query, context, allow_dynamic_relaxed=False):
        return [
            item for item in context
            if item.get("relevance_score", 0) >= MIN_STRONG_CONTEXT_SCORE
            or has_query_evidence(query, item["text"])
            or (
                allow_dynamic_relaxed
                and item["metadata"].get("domain") == "dynamic"
                and item.get("relevance_score", 0) >= MIN_DYNAMIC_CONTEXT_SCORE
            )
        ]

    def _format_context(self, context):
        context_text = ""
        for item in context:
            meta = item["metadata"]
            context_text += f"\n[Source: {meta['source']} | Credibility: {meta['credibility']} | Relevance: {item.get('relevance_score', 0):.2f}]\n{item['text']}\n"
        return context_text

    def _refresh_from_query(self, query):
        print("\n===== DYNAMIC SCRAPE =====")
        fresh_data = collect_market_data(
            query=query,
            max_articles=MAX_DYNAMIC_ARTICLES,
            sleep_seconds=0.25,
        )
        if not fresh_data: return False

        fresh_docs = self.retriever.documents_from_items(fresh_data)
        if not fresh_docs: return False

        seen = {doc["text"] for doc in self._documents}
        new_docs = [doc for doc in fresh_docs if doc["text"] not in seen]

        if not new_docs: return False

        self._documents.extend(new_docs)
        self.retriever.build_index(self._documents)
        return True

    def generate_response(self, query):
        if not self._initialized:
            raise RuntimeError("RAG pipeline is not initialized. Call initialize(file_path).")

        # STEP 1: PLAN (Dhruv's Architect Logic)
        plan = self.planner.plan(query)
        sub_queries = plan["sub_queries"]
        domain = plan["domain"]

        # STEP 2: RETRIEVE (Gaurav's RAG Logic)
        context = self._retrieve_context(sub_queries)
        if not context:
            if self._refresh_from_query(query):
                context = self._retrieve_context(sub_queries)

        if not context:
            return "No relevant data found."

        # STEP 3: FILTER & FORMAT (Dolly's Analysis Logic)
        relevant_context = self._filter_context(query, context)
        if not relevant_context:
            if self._refresh_from_query(query):
                context = self._retrieve_context(sub_queries)
                relevant_context = self._filter_context(query, context, allow_dynamic_relaxed=True)

        if not relevant_context:
            return "Insufficient data: no relevant evidence found."

        context_text = self._format_context(relevant_context)

        # STEP 4: PROMPT CONSTRUCTION
        system_prompt = f"You are a business intelligence analyst. Domain: {domain}. Use ONLY provided context."
        user_prompt = f"Context:\n{context_text}\n\nQuery: {query}"

        # STEP 5: GROQ CALL WITH RETRY
        for attempt in range(3):
            try:
                # Proper LangChain Groq Call
                response = self.llm.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ])
                
                if response and response.content:
                    return response.content
            except Exception as e:
                print(f"Groq Retry {attempt+1} failed: {e}")
                time.sleep(2)

        return "Model unavailable. Please try again later."