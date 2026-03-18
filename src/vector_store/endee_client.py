import numpy as np
from typing import List, Dict, Any, Optional
from config import config
import logging

logger = logging.getLogger(__name__)


class EndeeClient:
    

    def __init__(self):
        self.base_url = config.ENDEE_URL.rstrip("/")
        self.api_key  = config.ENDEE_API_KEY
        self.collection_name = config.ENDEE_COLLECTION_NAME
        self._client = None
        self._index  = None
        self._init_client()

    def _init_client(self):
        try:
            from endee import Endee
            if self.api_key:
                self._client = Endee(self.api_key)
            else:
                self._client = Endee()
            # Point to local server
            self._client.set_base_url(f"{self.base_url}/api/v1")
            logger.info("✅ Endee SDK client initialized at %s", self.base_url)
        except ImportError:
            logger.error("❌ endee package not installed. Run: pip install endee")
            self._client = None
        except Exception as e:
            logger.error("❌ Failed to initialize Endee client: %s", e)
            self._client = None

    def health_check(self) -> bool:
        if self._client is None:
            return False
        try:
            import requests
            r = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            if r.status_code == 200:
                logger.info("✅ Endee server healthy at %s", self.base_url)
                return True
            return False
        except Exception as e:
            logger.warning("⚠️  Endee not reachable: %s", e)
            return False

    def collection_exists(self) -> bool:
        if self._client is None:
            return False
        try:
            indexes = self._client.list_indexes()
            # indexes is a list of index info dicts or objects
            for idx in indexes:
                name = idx.get("name") if isinstance(idx, dict) else getattr(idx, "name", None)
                if name == self.collection_name:
                    logger.info("✅ Index '%s' exists", self.collection_name)
                    self._index = self._client.get_index(name=self.collection_name)
                    return True
            return False
        except Exception as e:
            logger.debug("collection_exists error: %s", e)
            return False

    def create_collection(self, dimension: int = None) -> bool:
        if self._client is None:
            return False
        if dimension is None:
            dimension = config.EMBEDDING_DIMENSION
        try:
            from endee import Precision
            self._client.create_index(
                name=self.collection_name,
                dimension=dimension,
                space_type="cosine",
                precision=Precision.INT8,
            )
            self._index = self._client.get_index(name=self.collection_name)
            logger.info("✅ Index '%s' created (dim=%d)", self.collection_name, dimension)
            return True
        except Exception as e:
            logger.error("❌ create_collection error: %s", e)
            # Index may already exist — try getting it
            try:
                self._index = self._client.get_index(name=self.collection_name)
                logger.info("✅ Using existing index '%s'", self.collection_name)
                return True
            except Exception:
                return False

    def _get_index(self):
        if self._index is None and self._client is not None:
            try:
                self._index = self._client.get_index(name=self.collection_name)
            except Exception as e:
                logger.error("❌ Cannot get index '%s': %s", self.collection_name, e)
        return self._index

    def insert_vector(self, vector_id: str, embedding: np.ndarray,
                      metadata: Dict[str, Any]) -> bool:
        index = self._get_index()
        if index is None:
            return False
        try:
            vector = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            index.upsert([{
                "id":     vector_id,
                "vector": vector,
                "meta":   metadata,
            }])
            logger.debug("✅ Vector '%s' upserted", vector_id)
            return True
        except Exception as e:
            logger.error("❌ insert_vector '%s' error: %s", vector_id, e)
            return False

    def insert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        index = self._get_index()
        if index is None:
            return False
        try:
            upsert_list = [
                {
                    "id":     v["id"],
                    "vector": v["vector"].tolist() if isinstance(v["vector"], np.ndarray) else v["vector"],
                    "meta":   v.get("metadata", {}),
                }
                for v in vectors
            ]
            index.upsert(upsert_list)
            logger.info("✅ Batch of %d vectors upserted", len(vectors))
            return True
        except Exception as e:
            logger.error("❌ insert_vectors error: %s", e)
            return False

    def search_similar(self, query_vector: np.ndarray,
                       top_k: int = None) -> List[Dict[str, Any]]:
        index = self._get_index()
        if index is None:
            return []
        if top_k is None:
            top_k = config.MAX_RESULTS
        try:
            vector = query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector
            raw = index.query(vector=vector, top_k=top_k)
            results = []
            for item in raw:
                if isinstance(item, dict):
                    results.append({
                        "id":       item.get("id", ""),
                        "score":    item.get("similarity", item.get("score", 0)),
                        "metadata": item.get("meta", item.get("metadata", {})),
                    })
                else:
                    results.append({
                        "id":       getattr(item, "id", ""),
                        "score":    getattr(item, "similarity", getattr(item, "score", 0)),
                        "metadata": getattr(item, "meta", {}),
                    })
            logger.info("✅ search_similar: %d results", len(results))
            return results
        except Exception as e:
            logger.error("❌ search_similar error: %s", e)
            return []

    def delete_vector(self, vector_id: str) -> bool:
        index = self._get_index()
        if index is None:
            return False
        try:
            index.delete_vector(vector_id)
            logger.info("✅ Vector '%s' deleted", vector_id)
            return True
        except Exception as e:
            logger.error("❌ delete_vector error: %s", e)
            return False
