
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LocalVectorStore:
    

    def __init__(self, collection_name: str = "support_tickets"):
        self.collection_name = collection_name
        # { vector_id: {"vector": np.ndarray, "metadata": dict} }
        self._store: Dict[str, Dict[str, Any]] = {}
        logger.info("🗄️  LocalVectorStore initialised (collection='%s')", collection_name)

    

    def health_check(self) -> bool:
        """Always healthy — it's in-memory."""
        return True

    def collection_exists(self) -> bool:
        return True   # always exists (it's just a dict)

    def create_collection(self, dimension: int = None) -> bool:
        logger.info("✅ LocalVectorStore: collection '%s' ready", self.collection_name)
        return True

    

    def insert_vector(self, vector_id: str, embedding: np.ndarray,
                      metadata: Dict[str, Any]) -> bool:
        try:
            vec = np.array(embedding, dtype=np.float32)
            # Normalise once at insert time — speeds up cosine search
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            self._store[vector_id] = {"vector": vec, "metadata": metadata}
            logger.debug("✅ LocalVectorStore: inserted '%s'", vector_id)
            return True
        except Exception as e:
            logger.error("❌ LocalVectorStore insert_vector error: %s", e)
            return False

    def insert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        success = sum(
            1 for v in vectors
            if self.insert_vector(
                v["id"],
                np.array(v["vector"]),
                v.get("metadata", {})
            )
        )
        return success == len(vectors)

    # ------------------------------------------------------------------ read

    def search_similar(self, query_vector: np.ndarray,
                       top_k: int = 5) -> List[Dict[str, Any]]:
        if not self._store:
            return []

        try:
            qvec = np.array(query_vector, dtype=np.float32)
            qnorm = np.linalg.norm(qvec)
            if qnorm > 0:
                qvec = qvec / qnorm

            scored = []
            for vid, entry in self._store.items():
                # Vectors are pre-normalised, so dot product == cosine similarity
                score = float(np.dot(qvec, entry["vector"]))
                scored.append({
                    "id":       vid,
                    "score":    score,
                    "metadata": entry["metadata"],
                })

            scored.sort(key=lambda x: x["score"], reverse=True)
            results = scored[:top_k]
            logger.info("✅ LocalVectorStore: found %d results", len(results))
            return results

        except Exception as e:
            logger.error("❌ LocalVectorStore search_similar error: %s", e)
            return []

    

    def delete_vector(self, vector_id: str) -> bool:
        removed = self._store.pop(vector_id, None)
        if removed:
            logger.info("✅ LocalVectorStore: deleted '%s'", vector_id)
        return True   # idempotent

    

    def get_stats(self) -> Dict[str, Any]:
        return {
            "backend":    "local_memory",
            "collection": self.collection_name,
            "count":      len(self._store),
        }
