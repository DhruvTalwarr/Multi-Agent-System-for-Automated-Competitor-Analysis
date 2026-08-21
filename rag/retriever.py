from rag.embedder import Embedder
from rag.vector_store import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import re
from datetime import datetime
from urllib.parse import urlparse


def get_source_credibility(source):
    mapping = {
        "data_gov": 0.95,
        "trai": 0.95,
        "rbi": 0.95,
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

    return source or "unknown"


def recency_score(timestamp):
    try:
        days_old = (datetime.now() - datetime.fromisoformat(timestamp)).days
    except (TypeError, ValueError):
        return 0.0

    return max(0, 1 - days_old / 365)


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "in", "is", "it", "of", "on", "or", "that", "the", "to", "what", "when",
    "where", "which", "who", "why", "with", "about", "can", "could", "should",
    "would", "will", "this", "these", "those", "any", "analyze", "analysis",
    "business", "companies", "company", "competitor", "competitors", "growth",
    "india", "indian", "industry", "latest", "market", "markets", "sector",
}


def tokenize(text):
    return [token for token in re.findall(r"\w+", text.lower()) if token not in STOPWORDS]


def lexical_overlap_score(query, text):
    query_tokens = set(tokenize(query))
    text_tokens = set(tokenize(text))

    if not query_tokens or not text_tokens:
        return 0.0

    return len(query_tokens & text_tokens) / len(query_tokens)


def has_query_evidence(query, text):
    query_tokens = set(tokenize(query))
    text_tokens = set(tokenize(text))

    if not query_tokens or not text_tokens:
        return False

    return bool(query_tokens & text_tokens)


BOILERPLATE_MARKERS = [
    "(Catch all the Business News",
    "Catch all the Business News",
    "Subscribe to The Economic Times",
    "Hot on Web",
    "In Case you missed it",
    "Find this comment offensive?",
    "Reason for reporting:",
    "15 Days Free:",
    "What\u2019s Included with",
    "What's Included with",
    "Offer Exclusively For You",
    "Investment Ideas",
    "Stock Reports Plus",
    "BigBull Portfolio",
    "Stock Analyzer",
    "Market Mood",
    "Download the Mint app",
    "Trump temper on H-1B visas",
    "What Adani",
    "New York Times Exclusives",
    "Docubay Subscription",
]


def clean_text(text):
    text = re.sub(r"\r\n?", "\n", str(text or ""))
    text = re.sub(r"[ \t]+", " ", text)

    cut_points = [
        text.find(marker)
        for marker in BOILERPLATE_MARKERS
        if text.find(marker) != -1
    ]
    if cut_points:
        text = text[:min(cut_points)]

    lines = []
    seen = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line in seen:
            continue
        seen.add(line)
        lines.append(line)

    return "\n".join(lines).strip()


def load_source_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        records = []
        for segment in re.split(r"\n\s*\n+", raw_text):
            cleaned = clean_text(segment)
            if len(cleaned) < 120:
                continue
            records.append({
                "text": cleaned,
                "source": "market_data_txt",
                "timestamp": datetime.now().isoformat(),
            })

        return records

    if isinstance(data, dict):
        data = data.get("articles") or data.get("data") or data.get("items") or [data]

    if not isinstance(data, list):
        raise ValueError("Market data must be a JSON object, JSON list, or plain text file.")

    return data


class Retriever:

    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = None

    def load_documents(self, file_path):
        data = load_source_data(file_path)
        return self.documents_from_items(data)

    def documents_from_items(self, data):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )

        documents = []

        for item in data:
            text = clean_text(item.get("text", ""))
            if not text:
                continue

            source = infer_source(item.get("source", "unknown"), item.get("url"))
            timestamp = item.get("timestamp") or datetime.now().isoformat()
            domain = item.get("domain")
            source_query = item.get("query")
            url = item.get("url")
            chunks = splitter.split_text(text)

            for chunk in chunks:
                documents.append({
                    "text": chunk,
                    "source": source,
                    "timestamp": timestamp,
                    "credibility": get_source_credibility(source),
                    "domain": domain,
                    "query": source_query,
                    "url": url
                })

        return documents

    def build_index(self, documents):
        if not documents:
            raise ValueError("No documents were provided to build the index.")

        texts = [doc["text"] for doc in documents]
        embeddings = self.embedder.encode(texts)

        dimension = len(embeddings[0])
        self.vector_store = VectorStore(dimension)

        metadata = []

        for i, doc in enumerate(documents):
            metadata.append({
                "chunk_id": i,
                "source": doc["source"],
                "timestamp": doc["timestamp"],
                "credibility": doc["credibility"],
                "domain": doc.get("domain"),
                "query": doc.get("query"),
                "url": doc.get("url")
            })

        self.vector_store.add_embeddings(embeddings, texts, metadata)
        self.vector_store.save()

    def retrieve(self, query, k=8):
        if self.vector_store is None:
            raise RuntimeError(
                "Retriever index is not initialized. Call initialize() or build_index() first."
            )

        results = []

        emb = self.embedder.encode([query])[0]
        results.extend(self.vector_store.search(emb, k=max(k * 3, 12)))

        # remove duplicates
        seen = set()
        unique = []

        for r in results:
            if r["text"] not in seen:
                unique.append(r)
                seen.add(r["text"])

        results = unique

        scored_results = []

        for item in results:
            meta = item["metadata"]

            sim_score = 1 / (1 + item["distance"])
            keyword_score = lexical_overlap_score(query, item["text"])

            score = (
                sim_score * 0.5 +
                keyword_score * 0.25 +
                meta["credibility"] * 0.15 +
                recency_score(meta["timestamp"]) * 0.10
            )

            item["relevance_score"] = score
            item["similarity_score"] = sim_score
            item["keyword_score"] = keyword_score
            scored_results.append((item, score))

        scored_results.sort(key=lambda x: x[1], reverse=True)

        # diversity
        final = []
        source_count = {}

        for item, score in scored_results:
            source = item["metadata"]["source"]

            if source_count.get(source, 0) < 2:
                final.append(item)
                source_count[source] = source_count.get(source, 0) + 1

            if len(final) == k:
                break

        return final
