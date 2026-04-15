import hashlib
import os
import re

import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initializes the embedding model.
        """
        self.model = None
        self._fallback_dimension = 384
        local_only = os.getenv("HF_LOCAL_FILES_ONLY", "1").lower() in {"1", "true", "yes"}

        try:
            self.model = SentenceTransformer(model_name, local_files_only=local_only)
        except Exception:
            self.model = None

    def _fallback_encode(self, texts):
        vectors = []

        for text in texts:
            vector = np.zeros(self._fallback_dimension, dtype=np.float32)
            tokens = re.findall(r"\w+", text.lower())

            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "little") % self._fallback_dimension
                vector[index] += 1.0

            norm = np.linalg.norm(vector)
            if norm > 0:
                vector /= norm

            vectors.append(vector)

        return np.array(vectors, dtype=np.float32)

    def encode(self, texts):
        """
        Convert text or list of texts into embeddings.
        """
        if isinstance(texts, str):
            texts = [texts]

        if self.model is not None:
            return self.model.encode(texts)

        return self._fallback_encode(texts)
