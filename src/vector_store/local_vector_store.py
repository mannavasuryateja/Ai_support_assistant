import numpy as np
import pickle
import os
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity

class LocalVectorStore:
    """Local vector storage for demo mode when Endee is not available."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.storage_path = f"data/{collection_name}_vectors.pkl"
        self.vectors = self._load_vectors()
    
    def _load_vectors(self) -> Dict[str, Any]:
        """Load vectors from local storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading vectors: {e}")
        return {"vectors": [], "metadata": [], "ids": []}
    
    def _save_vectors(self):
        """Save vectors to local storage."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, 'wb') as f:
                pickle.dump(self.vectors, f)
        except Exception as e:
            print(f"Error saving vectors: {e}")
    
    def insert_vector(self, vector_id: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Insert a vector with metadata."""
        try:
            # Check if vector already exists
            if vector_id in self.vectors["ids"]:
                # Update existing vector
                idx = self.vectors["ids"].index(vector_id)
                self.vectors["vectors"][idx] = embedding.tolist()
                self.vectors["metadata"][idx] = metadata
            else:
                # Add new vector
                self.vectors["vectors"].append(embedding.tolist())
                self.vectors["metadata"].append(metadata)
                self.vectors["ids"].append(vector_id)
            
            self._save_vectors()
            return True
        except Exception as e:
            print(f"Error inserting vector: {e}")
            return False
    
    def search_similar(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if not self.vectors["vectors"]:
            return []
        
        try:
            # Convert stored vectors to numpy array
            stored_vectors = np.array(self.vectors["vectors"])
            
            # Calculate cosine similarity
            similarities = cosine_similarity([query_vector], stored_vectors)[0]
            
            # Get top k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only return positive similarities
                    results.append({
                        "id": self.vectors["ids"][idx],
                        "score": float(similarities[idx]),
                        "metadata": self.vectors["metadata"][idx]
                    })
            
            return results
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector."""
        try:
            if vector_id in self.vectors["ids"]:
                idx = self.vectors["ids"].index(vector_id)
                del self.vectors["vectors"][idx]
                del self.vectors["metadata"][idx]
                del self.vectors["ids"][idx]
                self._save_vectors()
                return True
            return False
        except Exception as e:
            print(f"Error deleting vector: {e}")
            return False
    
    def collection_exists(self) -> bool:
        """Check if collection exists (always true for local storage)."""
        return True
    
    def create_collection(self, dimension: int = None) -> bool:
        """Create collection (always succeeds for local storage)."""
        return True