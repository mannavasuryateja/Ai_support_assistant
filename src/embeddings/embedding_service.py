from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
from config import config

class EmbeddingService:
    """Service for generating embeddings from text using sentence transformers."""
    
    def __init__(self):
        try:
            self.model = SentenceTransformer(config.EMBEDDING_MODEL)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"✅ Loaded embedding model: {config.EMBEDDING_MODEL}")
            print(f"📏 Embedding dimension: {self.dimension}")
        except Exception as e:
            print(f"❌ Failed to load sentence transformer: {e}")
            print("🔄 Falling back to simple TF-IDF embeddings")
            # Fallback to simple embeddings
            from .simple_embedding import SimpleEmbeddingService
            fallback = SimpleEmbeddingService()
            self.model = fallback
            self.dimension = 100  # TF-IDF dimension
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        try:
            if hasattr(self.model, 'encode'):
                # Sentence transformer
                embedding = self.model.encode(text, convert_to_numpy=True)
            else:
                # Fallback to simple embedding
                embedding = self.model.generate_embedding(text)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(self.dimension)
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        try:
            if hasattr(self.model, 'encode'):
                # Sentence transformer
                embeddings = self.model.encode(texts, convert_to_numpy=True)
            else:
                # Fallback to simple embedding
                embeddings = self.model.generate_embeddings(texts)
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return zero vectors as fallback
            return np.zeros((len(texts), self.dimension))
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text before embedding generation."""
        # Remove extra whitespace and normalize
        text = " ".join(text.split())
        return text.lower().strip()
    
    def embed_support_ticket(self, title: str, description: str, category: str = "") -> np.ndarray:
        """Generate embedding for a support ticket combining title, description, and category."""
        combined_text = f"{title} {description} {category}".strip()
        processed_text = self.preprocess_text(combined_text)
        return self.generate_embedding(processed_text)