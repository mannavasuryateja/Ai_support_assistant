import requests
import numpy as np
from typing import List, Dict, Any, Optional
from config import config
import json
import logging

logger = logging.getLogger(__name__)

class EndeeClient:
    """Client for interacting with Endee vector database via REST API."""
    
    def __init__(self):
        self.base_url = config.ENDEE_URL.rstrip('/')
        self.api_key = config.ENDEE_API_KEY
        self.collection_name = config.ENDEE_COLLECTION_NAME
        
        # Setup headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add authentication if token is provided
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def health_check(self) -> bool:
        """Check if Endee server is running and accessible."""
        try:
            # Try common health check endpoints
            health_endpoints = ["/health", "/status", "/ping", "/"]
            
            for endpoint in health_endpoints:
                try:
                    response = requests.get(
                        f"{self.base_url}{endpoint}", 
                        headers=self.headers,
                        timeout=5
                    )
                    if response.status_code in [200, 404]:  # 404 is OK, means server is running
                        logger.info(f"✅ Endee server is accessible at {self.base_url}")
                        return True
                except:
                    continue
            
            logger.warning(f"⚠️  Cannot reach Endee server at {self.base_url}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Endee health check failed: {e}")
            return False
    
    def create_collection(self, dimension: int = None) -> bool:
        """
        Create a new collection in Endee.
        
        Based on common vector database patterns, this creates an index/collection
        for storing vectors with the specified dimension.
        """
        if dimension is None:
            dimension = config.EMBEDDING_DIMENSION
        
        # Try different possible API endpoints for collection creation
        creation_endpoints = [
            {
                "url": f"{self.base_url}/collections",
                "payload": {
                    "name": self.collection_name,
                    "dimension": dimension,
                    "metric": "cosine",
                    "description": "Support tickets collection for semantic search"
                }
            },
            {
                "url": f"{self.base_url}/indexes",
                "payload": {
                    "name": self.collection_name,
                    "dimension": dimension,
                    "metric": "cosine"
                }
            },
            {
                "url": f"{self.base_url}/api/v1/collections",
                "payload": {
                    "collection_name": self.collection_name,
                    "dimension": dimension,
                    "distance_metric": "cosine"
                }
            }
        ]
        
        for endpoint_config in creation_endpoints:
            try:
                logger.info(f"🔧 Attempting to create collection at {endpoint_config['url']}")
                
                response = requests.post(
                    endpoint_config["url"],
                    headers=self.headers,
                    json=endpoint_config["payload"],
                    timeout=30
                )
                
                if response.status_code in [200, 201, 409]:  # 409 = already exists
                    if response.status_code == 409:
                        logger.info(f"✅ Collection '{self.collection_name}' already exists")
                    else:
                        logger.info(f"✅ Collection '{self.collection_name}' created successfully")
                    return True
                else:
                    logger.debug(f"Endpoint {endpoint_config['url']} returned {response.status_code}")
                    
            except Exception as e:
                logger.debug(f"Failed to create collection at {endpoint_config['url']}: {e}")
                continue
        
        logger.warning(f"⚠️  Could not create collection. This may be normal if Endee uses auto-creation.")
        return True  # Return True to allow the system to continue
    
    def collection_exists(self) -> bool:
        """Check if the collection exists."""
        check_endpoints = [
            f"{self.base_url}/collections/{self.collection_name}",
            f"{self.base_url}/indexes/{self.collection_name}",
            f"{self.base_url}/api/v1/collections/{self.collection_name}"
        ]
        
        for endpoint in check_endpoints:
            try:
                response = requests.get(endpoint, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ Collection '{self.collection_name}' exists")
                    return True
            except:
                continue
        
        logger.info(f"ℹ️  Collection existence check inconclusive - assuming it will be auto-created")
        return False
    
    def insert_vector(self, vector_id: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Insert a single vector with metadata into the collection."""
        
        # Prepare vector data in different possible formats
        vector_formats = [
            {
                "url": f"{self.base_url}/collections/{self.collection_name}/vectors",
                "payload": {
                    "id": vector_id,
                    "vector": embedding.tolist(),
                    "metadata": metadata
                }
            },
            {
                "url": f"{self.base_url}/vectors/upsert",
                "payload": {
                    "vectors": [{
                        "id": vector_id,
                        "values": embedding.tolist(),
                        "metadata": metadata
                    }],
                    "namespace": self.collection_name
                }
            },
            {
                "url": f"{self.base_url}/api/v1/vectors",
                "payload": {
                    "collection": self.collection_name,
                    "vectors": [{
                        "id": vector_id,
                        "vector": embedding.tolist(),
                        "metadata": metadata
                    }]
                }
            }
        ]
        
        for format_config in vector_formats:
            try:
                response = requests.post(
                    format_config["url"],
                    headers=self.headers,
                    json=format_config["payload"],
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    logger.debug(f"✅ Vector {vector_id} inserted successfully")
                    return True
                else:
                    logger.debug(f"Insert attempt at {format_config['url']} returned {response.status_code}")
                    
            except Exception as e:
                logger.debug(f"Insert failed at {format_config['url']}: {e}")
                continue
        
        logger.error(f"❌ Failed to insert vector {vector_id}")
        return False
    
    def insert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """Insert multiple vectors with metadata into the collection."""
        
        batch_formats = [
            {
                "url": f"{self.base_url}/collections/{self.collection_name}/vectors/batch",
                "payload": {"vectors": vectors}
            },
            {
                "url": f"{self.base_url}/vectors/upsert",
                "payload": {
                    "vectors": vectors,
                    "namespace": self.collection_name
                }
            },
            {
                "url": f"{self.base_url}/api/v1/vectors/batch",
                "payload": {
                    "collection": self.collection_name,
                    "vectors": vectors
                }
            }
        ]
        
        for format_config in batch_formats:
            try:
                response = requests.post(
                    format_config["url"],
                    headers=self.headers,
                    json=format_config["payload"],
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Batch of {len(vectors)} vectors inserted successfully")
                    return True
                    
            except Exception as e:
                logger.debug(f"Batch insert failed at {format_config['url']}: {e}")
                continue
        
        logger.error(f"❌ Failed to insert batch of {len(vectors)} vectors")
        return False
    
    def search_similar(self, query_vector: np.ndarray, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar vectors in the collection."""
        if top_k is None:
            top_k = config.MAX_RESULTS
        
        search_formats = [
            {
                "url": f"{self.base_url}/collections/{self.collection_name}/search",
                "payload": {
                    "vector": query_vector.tolist(),
                    "top_k": top_k,
                    "include_metadata": True
                }
            },
            {
                "url": f"{self.base_url}/query",
                "payload": {
                    "namespace": self.collection_name,
                    "vector": query_vector.tolist(),
                    "top_k": top_k,
                    "include_metadata": True
                }
            },
            {
                "url": f"{self.base_url}/api/v1/search",
                "payload": {
                    "collection": self.collection_name,
                    "query_vector": query_vector.tolist(),
                    "limit": top_k,
                    "include_metadata": True
                }
            }
        ]
        
        for format_config in search_formats:
            try:
                response = requests.post(
                    format_config["url"],
                    headers=self.headers,
                    json=format_config["payload"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Try different response formats
                    results = []
                    if "matches" in data:
                        results = data["matches"]
                    elif "results" in data:
                        results = data["results"]
                    elif "vectors" in data:
                        results = data["vectors"]
                    elif isinstance(data, list):
                        results = data
                    
                    # Normalize result format
                    normalized_results = []
                    for result in results:
                        normalized_result = {
                            "id": result.get("id", result.get("vector_id", "")),
                            "score": result.get("score", result.get("similarity", result.get("distance", 0))),
                            "metadata": result.get("metadata", result.get("payload", {}))
                        }
                        normalized_results.append(normalized_result)
                    
                    logger.info(f"✅ Found {len(normalized_results)} similar vectors")
                    return normalized_results
                    
            except Exception as e:
                logger.debug(f"Search failed at {format_config['url']}: {e}")
                continue
        
        logger.warning(f"⚠️  Search failed - returning empty results")
        return []
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from the collection."""
        delete_endpoints = [
            f"{self.base_url}/collections/{self.collection_name}/vectors/{vector_id}",
            f"{self.base_url}/vectors/delete/{vector_id}",
            f"{self.base_url}/api/v1/vectors/{vector_id}"
        ]
        
        for endpoint in delete_endpoints:
            try:
                response = requests.delete(endpoint, headers=self.headers, timeout=10)
                if response.status_code in [200, 204, 404]:  # 404 = already deleted
                    logger.info(f"✅ Vector {vector_id} deleted")
                    return True
            except Exception as e:
                logger.debug(f"Delete failed at {endpoint}: {e}")
                continue
        
        logger.error(f"❌ Failed to delete vector {vector_id}")
        return False
        self.collection_exists_flag = False
    
    def create_collection(self, dimension: int = None) -> bool:
        """Create a new collection in Endee."""
        if dimension is None:
            dimension = config.EMBEDDING_DIMENSION
            
        try:
            self.collection_exists_flag = True
            print(f"Mock: Created collection '{self.collection_name}' with dimension {dimension}")
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
    
    def insert_vector(self, vector_id: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Insert a single vector with metadata into the collection."""
        try:
            self.vectors[vector_id] = {
                "vector": embedding,
                "metadata": metadata
            }
            print(f"Mock: Inserted vector {vector_id}")
            return True
        except Exception as e:
            print(f"Error inserting vector: {e}")
            return False
    
    def insert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """Insert multiple vectors with metadata into the collection."""
        try:
            for vector_data in vectors:
                vector_id = vector_data["id"]
                embedding = np.array(vector_data["vector"])
                metadata = vector_data["metadata"]
                self.vectors[vector_id] = {
                    "vector": embedding,
                    "metadata": metadata
                }
            print(f"Mock: Inserted {len(vectors)} vectors")
            return True
        except Exception as e:
            print(f"Error inserting vectors: {e}")
            return False
    
    def search_similar(self, query_vector: np.ndarray, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar vectors in the collection."""
        if top_k is None:
            top_k = config.MAX_RESULTS
            
        try:
            if not self.vectors:
                return []
            
            # Calculate similarities
            similarities = []
            for vector_id, data in self.vectors.items():
                stored_vector = data["vector"]
                # Calculate cosine similarity
                similarity = cosine_similarity(
                    query_vector.reshape(1, -1),
                    stored_vector.reshape(1, -1)
                )[0][0]
                
                similarities.append({
                    "id": vector_id,
                    "score": float(similarity),
                    "metadata": data["metadata"]
                })
            
            # Sort by similarity score (descending)
            similarities.sort(key=lambda x: x["score"], reverse=True)
            
            # Return top_k results
            results = similarities[:top_k]
            print(f"Mock: Found {len(results)} similar vectors")
            return results
            
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from the collection."""
        try:
            if vector_id in self.vectors:
                del self.vectors[vector_id]
                print(f"Mock: Deleted vector {vector_id}")
                return True
            return False
        except Exception as e:
            print(f"Error deleting vector: {e}")
            return False
    
    def collection_exists(self) -> bool:
        """Check if the collection exists."""
        return self.collection_exists_flag