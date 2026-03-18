import numpy as np
from typing import List, Union
from config import config

try:
    from sentence_transformers import SentenceTransformer
    _HAS_SENTENCE_TRANSFORMERS = True
except Exception:
    _HAS_SENTENCE_TRANSFORMERS = False

class EmbeddingService:
   
    
    def __init__(self):
        if _HAS_SENTENCE_TRANSFORMERS:
            try:
                self.model = SentenceTransformer(config.EMBEDDING_MODEL)
                self.dimension = self.model.get_sentence_embedding_dimension()
                print(f"✅ Loaded embedding model: {config.EMBEDDING_MODEL}")
                print(f"📏 Embedding dimension: {self.dimension}")
            except Exception as e:
                print(f"❌ Failed to load sentence transformer: {e}")
                print("🔄 Falling back to simple TF-IDF embeddings")
                from .simple_embedding import SimpleEmbeddingService
                self.model = SimpleEmbeddingService()
                self.dimension = 100
        else:
            print("⚠️ sentence-transformers unavailable; using simple TF-IDF fallback.")
            from .simple_embedding import SimpleEmbeddingService
            self.model = SimpleEmbeddingService()
            self.dimension = 100
    
    def generate_embedding(self, text: str) -> np.ndarray:
        
        try:
            if hasattr(self.model, 'encode'):
                
                embedding = self.model.encode(text, convert_to_numpy=True)
            else:
                
                embedding = self.model.generate_embedding(text)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            
            return np.zeros(self.dimension)
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        
        try:
            if hasattr(self.model, 'encode'):
                embeddings = self.model.encode(texts, convert_to_numpy=True)
            else:
                embeddings = self.model.generate_embeddings(texts)
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return np.zeros((len(texts), self.dimension))
    
    def preprocess_text(self, text: str) -> str:
        text = " ".join(text.split())
        return text.lower().strip()
    
    def embed_support_ticket(self, title: str, description: str, category: str = "") -> np.ndarray:
        """Generate embedding for a support ticket combining title, description, and category."""
        combined_text = f"{title} {description} {category}".strip()
        processed_text = self.preprocess_text(combined_text)
        return self.generate_embedding(processed_text)
