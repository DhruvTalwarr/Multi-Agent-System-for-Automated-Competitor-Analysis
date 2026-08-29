
#vector_store.py
import faiss
import numpy as np
import pickle


class VectorStore:

    def __init__(self, dimension):
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadata=[]

    def _normalize(self, embeddings):
        embeddings = np.array(embeddings).astype("float32")
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return embeddings / norms

    def add_embeddings(self, embeddings, docs,metadata=None):

        embeddings = self._normalize(embeddings)
        self.index.add(embeddings)
        self.documents.extend(docs)
        if metadata is None:
            metadata = [{} for _ in docs]
        self.metadata.extend(metadata)

    def search(self, query_embedding, k=5):

        query_embedding = self._normalize([query_embedding])

        distances, indices = self.index.search(query_embedding, k)

        results = []

        for i,idx in enumerate(indices[0]):

            if 0 <= idx < len(self.documents):

                results.append({
                    "text": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "distance":float(distances[0][i])
                })

        return results

    def save(self, index_path="faiss_index.index", docs_path="docs.pkl", meta_path="meta.pkl"):

        faiss.write_index(self.index, index_path)

        with open(docs_path, "wb") as f:
            pickle.dump(self.documents, f)

        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self, index_path="faiss_index.index", docs_path="docs.pkl", meta_path="meta.pkl"):

        self.index = faiss.read_index(index_path)

        with open(docs_path, "rb") as f:
            self.documents = pickle.load(f)

        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
