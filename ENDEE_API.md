# Endee Vector Database API Integration

This document outlines the Endee vector database API endpoints used by the AI Support Assistant and provides examples of how to interact with Endee directly.

## 🔧 Endee API Endpoints

Our EndeeClient supports multiple possible API formats to ensure compatibility with different Endee configurations:

### 1. Collection Management

#### Create Collection
```bash
# Format 1: Standard collections endpoint
POST /collections
{
  "name": "support_tickets",
  "dimension": 384,
  "metric": "cosine",
  "description": "Support tickets collection for semantic search"
}

# Format 2: Index-based endpoint
POST /indexes
{
  "name": "support_tickets", 
  "dimension": 384,
  "metric": "cosine"
}

# Format 3: Versioned API
POST /api/v1/collections
{
  "collection_name": "support_tickets",
  "dimension": 384,
  "distance_metric": "cosine"
}
```

#### Check Collection Exists
```bash
GET /collections/{collection_name}
GET /indexes/{collection_name}
GET /api/v1/collections/{collection_name}
```

### 2. Vector Operations

#### Insert Single Vector
```bash
# Format 1: Collection-based
POST /collections/{collection_name}/vectors
{
  "id": "ticket_001",
  "vector": [0.1, 0.2, 0.3, ...],
  "metadata": {
    "title": "Cannot login to account",
    "category": "authentication",
    "resolution": "Password reset required"
  }
}

# Format 2: Pinecone-style upsert
POST /vectors/upsert
{
  "vectors": [{
    "id": "ticket_001",
    "values": [0.1, 0.2, 0.3, ...],
    "metadata": {...}
  }],
  "namespace": "support_tickets"
}

# Format 3: Versioned API
POST /api/v1/vectors
{
  "collection": "support_tickets",
  "vectors": [{
    "id": "ticket_001",
    "vector": [0.1, 0.2, 0.3, ...],
    "metadata": {...}
  }]
}
```

#### Batch Insert Vectors
```bash
# Format 1: Batch endpoint
POST /collections/{collection_name}/vectors/batch
{
  "vectors": [
    {
      "id": "ticket_001",
      "vector": [0.1, 0.2, ...],
      "metadata": {...}
    },
    {
      "id": "ticket_002", 
      "vector": [0.4, 0.5, ...],
      "metadata": {...}
    }
  ]
}

# Format 2: Upsert multiple
POST /vectors/upsert
{
  "vectors": [...],
  "namespace": "support_tickets"
}
```

### 3. Vector Search

#### Similarity Search
```bash
# Format 1: Collection search
POST /collections/{collection_name}/search
{
  "vector": [0.1, 0.2, 0.3, ...],
  "top_k": 5,
  "include_metadata": true
}

# Format 2: Query endpoint
POST /query
{
  "namespace": "support_tickets",
  "vector": [0.1, 0.2, 0.3, ...],
  "top_k": 5,
  "include_metadata": true
}

# Format 3: Versioned search
POST /api/v1/search
{
  "collection": "support_tickets",
  "query_vector": [0.1, 0.2, 0.3, ...],
  "limit": 5,
  "include_metadata": true
}
```

#### Search Response Formats
```json
// Format 1: Matches array
{
  "matches": [
    {
      "id": "ticket_001",
      "score": 0.95,
      "metadata": {...}
    }
  ]
}

// Format 2: Results array  
{
  "results": [
    {
      "vector_id": "ticket_001",
      "similarity": 0.95,
      "payload": {...}
    }
  ]
}

// Format 3: Direct array
[
  {
    "id": "ticket_001",
    "distance": 0.05,
    "metadata": {...}
  }
]
```

### 4. Vector Management

#### Delete Vector
```bash
DELETE /collections/{collection_name}/vectors/{vector_id}
DELETE /vectors/delete/{vector_id}
DELETE /api/v1/vectors/{vector_id}
```

### 5. Health Check

#### Server Health
```bash
GET /health
GET /status  
GET /ping
GET /
```

## 🚀 Usage Examples

### Python Client Example
```python
import requests
import numpy as np

# Initialize client
base_url = "http://localhost:8080"
headers = {"Content-Type": "application/json"}

# Create collection
collection_data = {
    "name": "support_tickets",
    "dimension": 384,
    "metric": "cosine"
}
response = requests.post(f"{base_url}/collections", json=collection_data, headers=headers)

# Insert vector
vector_data = {
    "id": "ticket_001",
    "vector": np.random.rand(384).tolist(),
    "metadata": {
        "title": "Login issue",
        "category": "authentication"
    }
}
response = requests.post(f"{base_url}/collections/support_tickets/vectors", 
                        json=vector_data, headers=headers)

# Search similar vectors
search_data = {
    "vector": np.random.rand(384).tolist(),
    "top_k": 5,
    "include_metadata": True
}
response = requests.post(f"{base_url}/collections/support_tickets/search",
                        json=search_data, headers=headers)
results = response.json()
```

### cURL Examples
```bash
# Create collection
curl -X POST http://localhost:8080/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "support_tickets",
    "dimension": 384,
    "metric": "cosine"
  }'

# Insert vector
curl -X POST http://localhost:8080/collections/support_tickets/vectors \
  -H "Content-Type: application/json" \
  -d '{
    "id": "ticket_001",
    "vector": [0.1, 0.2, 0.3],
    "metadata": {"title": "Test ticket"}
  }'

# Search vectors
curl -X POST http://localhost:8080/collections/support_tickets/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3],
    "top_k": 5,
    "include_metadata": true
  }'
```

## 🔐 Authentication

If Endee requires authentication, add the token to headers:

```python
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_token_here"
}
```

## ⚙️ Configuration

Set these environment variables:

```bash
ENDEE_URL=http://localhost:8080
ENDEE_API_KEY=your_token_here  # Optional
ENDEE_COLLECTION_NAME=support_tickets
```

## 🔍 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Endee server is running: `docker ps | grep endee`
   - Check URL is correct: `curl http://localhost:8080/health`

2. **Collection Not Found**
   - Create collection first before inserting vectors
   - Check collection name matches exactly

3. **Dimension Mismatch**
   - Ensure all vectors have same dimension (384 for our model)
   - Verify embedding model output dimension

4. **Authentication Errors**
   - Check if Endee requires authentication
   - Verify API key is correct and not expired

### Debug Mode

Enable debug logging to see all API attempts:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📊 Performance Tips

1. **Batch Operations**: Use batch insert for multiple vectors
2. **Connection Pooling**: Reuse HTTP connections
3. **Async Requests**: Use async HTTP client for better performance
4. **Caching**: Cache frequent search results
5. **Indexing**: Ensure proper indexing for large datasets

## 🔄 Fallback Strategy

Our system automatically falls back to local storage if Endee is unavailable:

1. **Health Check**: Tests Endee connectivity
2. **Auto-Fallback**: Switches to local vector store
3. **Seamless Operation**: Same API, different backend
4. **Easy Migration**: Can switch back when Endee is available

This ensures your application works regardless of Endee availability!