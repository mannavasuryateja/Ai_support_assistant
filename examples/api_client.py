"""
Example API client for the AI-Powered Support Assistant.
This demonstrates how to interact with the REST API.
"""

import requests
import json
from typing import Dict, Any

class SupportAssistantClient:
    """Client for interacting with the Support Assistant API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy."""
        response = requests.get(f"{self.api_base}/health")
        return response.json()
    
    def initialize_system(self) -> Dict[str, Any]:
        """Initialize the support system."""
        response = requests.post(f"{self.api_base}/initialize")
        return response.json()
    
    def query_support(self, query: str, category: str = None, max_results: int = 5) -> Dict[str, Any]:
        """Submit a support query."""
        payload = {
            "query": query,
            "max_results": max_results
        }
        if category:
            payload["category"] = category
        
        response = requests.post(f"{self.api_base}/query", json=payload)
        return response.json()
    
    def add_tickets(self, tickets: list) -> Dict[str, Any]:
        """Add new support tickets."""
        payload = {"tickets": tickets}
        response = requests.post(f"{self.api_base}/tickets", json=payload)
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        response = requests.get(f"{self.api_base}/stats")
        return response.json()

def main():
    """Demonstrate API client usage."""
    client = SupportAssistantClient()
    
    print("AI Support Assistant API Client Demo\n")
    
    # Health check
    print("1. Health Check:")
    try:
        health = client.health_check()
        print(f"Status: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Initialize system
    print("\n2. Initializing System:")
    try:
        init_result = client.initialize_system()
        print(f"Result: {init_result.get('message', 'unknown')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test queries
    print("\n3. Testing Support Queries:")
    test_queries = [
        ("I forgot my password", "authentication"),
        ("Payment not working", "billing"),
        ("App is slow", "performance")
    ]
    
    for query, category in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = client.query_support(query, category)
            print(f"Action: {result.get('action', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 0):.2f}")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Processing time: {result.get('processing_time', 0):.3f}s")
        except Exception as e:
            print(f"Error: {e}")
    
    # Add new tickets
    print("\n4. Adding New Tickets:")
    new_tickets = [
        {
            "id": "demo_001",
            "title": "API integration issues",
            "description": "Having trouble integrating with the REST API",
            "category": "technical",
            "status": "open",
            "priority": "medium"
        }
    ]
    
    try:
        result = client.add_tickets(new_tickets)
        print(f"Inserted: {result.get('inserted_count', 0)}")
        print(f"Failed: {result.get('failed_count', 0)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Get stats
    print("\n5. System Statistics:")
    try:
        stats = client.get_stats()
        print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()