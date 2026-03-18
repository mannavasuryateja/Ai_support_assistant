import numpy as np
from typing import List
import re

class SimpleEmbeddingService:
    

    def __init__(self):
        self.dimension = 100

    def preprocess_text(self, text: str) -> str:
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = ' '.join(text.split())
        return text.lower()

    def _hash_vector(self, text: str) -> np.ndarray:
        text = self.preprocess_text(text)
        vector = np.zeros(self.dimension, dtype=float)
        for i, token in enumerate(text.split()):
            idx = abs(hash(token)) % self.dimension
            vector[idx] += 1.0 / (1 + i)

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        return vector

    def generate_embedding(self, text: str) -> np.ndarray:
        return self._hash_vector(text)

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        return np.vstack([self.generate_embedding(t) for t in texts])

    def embed_support_ticket(self, title: str, description: str, category: str = "") -> np.ndarray:
        combined_text = f"{title} {description} {category}".strip()
        return self.generate_embedding(combined_text)
