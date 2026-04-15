from rag.embedder import Embedder
from rag.vector_store import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import re
import numpy as np
from datetime import datetime
from urllib.parse import urlparse


# ------------------ SOURCE SCORING ------------------

def get_source_credibility(source):
    mapping = {
        "data_gov": 0.95,
        "trai": 0.95,
        "rbi": 0.95,
        "sebi": 0.95,
        "ministry_of_finance": 0.95,
        "business_standard": 0.85,
        "livemint": 0.8,
        "economic_times": 0.75,
        "moneycontrol": 0.75,
        "google_news": 0.7,
        "news": 0.7,
        "unknown": 0.5
    }
    return mapping.get(source, 0.5)


def infer_source(source, url=None):
    if source and source not in {"news", "unknown"}:
        return source

    domain = urlparse(url or "").netloc.lower()

    if "economictimes" in domain:
        return "economic_times"
    if "livemint" in domain:
        return "livemint"
    if "moneycontrol" in domain:
        return "moneycontrol"
    if "business-standard" in domain:
        return "business_standard"
    if "news.google" in domain:
        return "google_news"
    if "rbi.org.in" in domain:
        return "rbi"
    if "sebi.gov.in" in domain:
        return "sebi"
    if "finmin.gov.in" in domain:
        return "ministry_of_finance"
    if "data.gov.in" in domain:
        return "data_gov"
    if "trai.gov.in" in domain:
        return "trai"

    return source or "unknown"


def recency_score(timestamp):
    try:
        days_old = (datetime.now() - datetime.fromisoformat(timestamp)).days
    except:
        return 0.0

    return max(0, 1 - days_old / 365)


# ------------------ TEXT PROCESSING ------------------

STOPWORDS = {
    "a","an","and","are","as","at","be","by","for","from","how",
    "in","is","it","of","on","or","that","the","to","what","when",
    "where","which","who","why","with","about","can","could","should",
    "would","will","this","these","those","any","analyze","analysis",
    "business","companies","company","competitor","competitors","growth",
    "india","indian","industry","latest","market","markets","sector",
}


def tokenize(text):
    return [t for t in re.findall(r"\w+", text.lower()) if t not in STOPWORDS]


def lexical_overlap_score(query, text):
    q_tokens = set(tokenize(query))
    t_tokens = set(tokenize(text))

    if not q_tokens or not t_tokens:
        return 0.0

    return len(q_tokens & t_tokens) / len(q_tokens)


# ------------------ CLEANING ------------------

def clean_text(text):
    text = re.sub(r"\r\n?", "\n", str(text or ""))
    text = re.sub(r"[ \t]+", " ", text)

    # remove very short/noisy text
    if len(text) < 100:
        return ""

    return text.strip()


# ------------------ LOADER ------------------

def load_source_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = data.get("articles") or data.get("data") or data.get("items") or [data]

    return data


# ------------------ RETRIEVER ------------------

class Retriever:

    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = None
        self.documents = []

    def documents_from_items(self, data):
        docs = []

        for item in data:
            text = clean_text(item.get("text", ""))
            if not text:
                continue

            source = infer_source(
                item.get("source") or item.get("metadata", {}).get("source"),
                item.get("url")
            )

            credibility = get_source_credibility(source)

            docs.append({
                "text": text,
                "metadata": {
                    "source": source,
                    "credibility": credibility,
                    "timestamp": item.get("timestamp", datetime.now().isoformat()),
                    "domain": item.get("domain", "general")
                }
            })

        return docs

    def load_documents(self, file_path):
        raw_data = load_source_data(file_path)

        docs = []

        for item in raw_data:
            text = clean_text(item.get("text", ""))
            if not text:
                continue

            source = infer_source(item.get("source"), item.get("url"))
            credibility = get_source_credibility(source)

            docs.append({
                "text": text,
                "metadata": {
                    "source": source,
                    "credibility": credibility,
                    "timestamp": item.get("timestamp", datetime.now().isoformat()),
                    "domain": item.get("domain", "general")
                }
            })

        return docs

    def build_index(self, docs):
        self.documents = docs

        texts = [d["text"] for d in docs]
        metadata = [d["metadata"] for d in docs]

        embeddings = self.embedder.encode(texts)

        dimension = len(embeddings[0])
        self.vector_store = VectorStore(dimension)

        self.vector_store.add_embeddings(embeddings, texts, metadata)

    def retrieve(self, query, k=5):

        query_embedding = self.embedder.encode([query])[0]
        results = self.vector_store.search(query_embedding, k=k)

        final_results = []

        for item in results:

            semantic_score = item["score"]  # ✅ FIXED
            lexical_score = lexical_overlap_score(query, item["text"])
            recency = recency_score(item["metadata"].get("timestamp", ""))
            credibility = item["metadata"].get("credibility", 0.5)

            # 🔥 FINAL COMBINED SCORE
            relevance_score = (
                0.5 * semantic_score +
                0.2 * lexical_score +
                0.15 * recency +
                0.15 * credibility
            )

            final_results.append({
                "text": item["text"],
                "metadata": item["metadata"],
                "score": semantic_score,
                "relevance_score": relevance_score
            })

        # 🔥 SORT BY RELEVANCE
        final_results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return final_results