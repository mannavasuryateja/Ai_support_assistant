import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import re

class SimpleEmbeddingService:
    """Simple embedding service using TF-IDF for demo purposes."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        self.is_fitted = False
        
        # Pre-fit with common support terms
        sample_texts = [
            "login password authentication account access",
            "payment billing credit card declined",
            "app crash technical error bug",
            "slow loading performance website",
            "email notification settings",
            "file upload download error",
            "search function not working"
        ]
        self.vectorizer.fit(sample_texts)
        self.is_fitted = True
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text."""
        # Remove special characters and extra spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = ' '.join(text.split())
        return text.lower()
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate TF-IDF embedding for text."""
        processed_text = self.preprocess_text(text)
        
        if not self.is_fitted:
            # Fit on the single text if not already fitted
            self.vectorizer.fit([processed_text])
            self.is_fitted = True
        
        embedding = self.vectorizer.transform([processed_text]).toarray()[0]
        return embedding
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        if not self.is_fitted:
            self.vectorizer.fit(processed_texts)
            self.is_fitted = True
        
        embeddings = self.vectorizer.transform(processed_texts).toarray()
        return embeddings
    
    def embed_support_ticket(self, title: str, description: str, category: str = "") -> np.ndarray:
        """Generate embedding for a support ticket."""
        combined_text = f"{title} {description} {category}".strip()
        return self.generate_embedding(combined_text)