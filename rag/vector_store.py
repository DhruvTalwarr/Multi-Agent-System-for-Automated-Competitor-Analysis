import faiss
import numpy as np
import pickle


class VectorStore:

    def __init__(self, dimension):
        # 🔥 USE INNER PRODUCT (better for cosine similarity)
        self.index = faiss.IndexFlatIP(dimension)

        self.documents = []
        self.metadata = []

    # ---------------- NORMALIZATION ----------------

    def _normalize(self, embeddings):
        embeddings = np.array(embeddings).astype("float32")
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return embeddings / norms

    # ---------------- ADD ----------------

    def add_embeddings(self, embeddings, docs, metadata=None):

        embeddings = self._normalize(embeddings)

        self.index.add(embeddings)
        self.documents.extend(docs)

        if metadata is None:
            metadata = [{} for _ in docs]

        self.metadata.extend(metadata)

    # ---------------- SEARCH ----------------

    def search(self, query_embedding, k=5, filter_fn=None):

        query_embedding = self._normalize([query_embedding])

        scores, indices = self.index.search(query_embedding, k * 3)

        results = []

        for i, idx in enumerate(indices[0]):

            if idx < 0 or idx >= len(self.documents):
                continue

            item = {
                "text": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(scores[0][i])  # 🔥 cosine similarity directly
            }

            # 🔥 optional filtering (domain / source)
            if filter_fn and not filter_fn(item):
                continue

            results.append(item)

            if len(results) >= k:
                break

        return results

    # ---------------- SAVE ----------------

    def save(
        self,
        index_path="faiss_index.index",
        docs_path="docs.pkl",
        meta_path="meta.pkl"
    ):
        faiss.write_index(self.index, index_path)

        with open(docs_path, "wb") as f:
            pickle.dump(self.documents, f)

        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    # ---------------- LOAD ----------------

    def load(
        self,
        index_path="faiss_index.index",
        docs_path="docs.pkl",
        meta_path="meta.pkl"
    ):
        self.index = faiss.read_index(index_path)

        with open(docs_path, "rb") as f:
            self.documents = pickle.load(f)

        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)