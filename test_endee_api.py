#!/usr/bin/env python3
"""
Test script for Endee Vector Database API endpoints
This script tests various API formats to ensure compatibility
"""

import requests
import numpy as np
import json
import time
from typing import Dict, Any, List

class EndeeAPITester:
    """Test different Endee API endpoint formats."""
    
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def test_health_check(self) -> bool:
        """Test if Endee server is accessible."""
        print("🔍 Testing Endee server health...")
        
        health_endpoints = ["/health", "/status", "/ping", "/"]
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", 
                                      headers=self.headers, timeout=5)
                print(f"  {endpoint}: {response.status_code}")
                
                if response.status_code in [200, 404]:
                    print(f"✅ Server accessible at {self.base_url}")
                    return True
            except Exception as e:
                print(f"  {endpoint}: Failed - {e}")
        
        print(f"❌ Server not accessible at {self.base_url}")
        return False
    
    def test_create_collection(self, collection_name: str = "test_collection", 
                             dimension: int = 384) -> bool:
        """Test collection creation with different API formats."""
        print(f"\n🔧 Testing collection creation: {collection_name}")
        
        creation_formats = [
            {
                "name": "Standard Collections API",
                "url": f"{self.base_url}/collections",
                "payload": {
                    "name": collection_name,
                    "dimension": dimension,
                    "metric": "cosine",
                    "description": "Test collection"
                }
            },
            {
                "name": "Index API",
                "url": f"{self.base_url}/indexes",
                "payload": {
                    "name": collection_name,
                    "dimension": dimension,
                    "metric": "cosine"
                }
            },
            {
                "name": "Versioned API",
                "url": f"{self.base_url}/api/v1/collections",
                "payload": {
                    "collection_name": collection_name,
                    "dimension": dimension,
                    "distance_metric": "cosine"
                }
            }
        ]
        
        for format_config in creation_formats:
            try:
                print(f"  Testing {format_config['name']}...")
                response = requests.post(
                    format_config["url"],
                    headers=self.headers,
                    json=format_config["payload"],
                    timeout=10
                )
                
                print(f"    Status: {response.status_code}")
                if response.text:
                    print(f"    Response: {response.text[:200]}...")
                
                if response.status_code in [200, 201, 409]:
                    print(f"  ✅ {format_config['name']} - Success")
                    return True
                    
            except Exception as e:
                print(f"  ❌ {format_config['name']} - Error: {e}")
        
        print("⚠️  Collection creation failed - may use auto-creation")
        return False
    
    def test_insert_vector(self, collection_name: str = "test_collection") -> bool:
        """Test vector insertion with different API formats."""
        print(f"\n📝 Testing vector insertion into: {collection_name}")
        
        # Generate test vector
        test_vector = np.random.rand(384).tolist()
        test_metadata = {
            "title": "Test Support Ticket",
            "category": "test",
            "description": "This is a test ticket for API validation"
        }
        
        insertion_formats = [
            {
                "name": "Collection Vectors API",
                "url": f"{self.base_url}/collections/{collection_name}/vectors",
                "payload": {
                    "id": "test_001",
                    "vector": test_vector,
                    "metadata": test_metadata
                }
            },
            {
                "name": "Upsert API",
                "url": f"{self.base_url}/vectors/upsert",
                "payload": {
                    "vectors": [{
                        "id": "test_001",
                        "values": test_vector,
                        "metadata": test_metadata
                    }],
                    "namespace": collection_name
                }
            },
            {
                "name": "Versioned Vectors API",
                "url": f"{self.base_url}/api/v1/vectors",
                "payload": {
                    "collection": collection_name,
                    "vectors": [{
                        "id": "test_001",
                        "vector": test_vector,
                        "metadata": test_metadata
                    }]
                }
            }
        ]
        
        for format_config in insertion_formats:
            try:
                print(f"  Testing {format_config['name']}...")
                response = requests.post(
                    format_config["url"],
                    headers=self.headers,
                    json=format_config["payload"],
                    timeout=10
                )
                
                print(f"    Status: {response.status_code}")
                if response.text:
                    print(f"    Response: {response.text[:200]}...")
                
                if response.status_code in [200, 201]:
                    print(f"  ✅ {format_config['name']} - Success")
                    return True
                    
            except Exception as e:
                print(f"  ❌ {format_config['name']} - Error: {e}")
        
        print("❌ Vector insertion failed")
        return False
    
    def test_search_vectors(self, collection_name: str = "test_collection") -> bool:
        """Test vector search with different API formats."""
        print(f"\n🔍 Testing vector search in: {collection_name}")
        
        # Generate test query vector
        query_vector = np.random.rand(384).tolist()
        
        search_formats = [
            {
                "name": "Collection Search API",
                "url": f"{self.base_url}/collections/{collection_name}/search",
                "payload": {
                    "vector": query_vector,
                    "top_k": 5,
                    "include_metadata": True
                }
            },
            {
                "name": "Query API",
                "url": f"{self.base_url}/query",
                "payload": {
                    "namespace": collection_name,
                    "vector": query_vector,
                    "top_k": 5,
                    "include_metadata": True
                }
            },
            {
                "name": "Versioned Search API",
                "url": f"{self.base_url}/api/v1/search",
                "payload": {
                    "collection": collection_name,
                    "query_vector": query_vector,
                    "limit": 5,
                    "include_metadata": True
                }
            }
        ]
        
        for format_config in search_formats:
            try:
                print(f"  Testing {format_config['name']}...")
                response = requests.post(
                    format_config["url"],
                    headers=self.headers,
                    json=format_config["payload"],
                    timeout=10
                )
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    Response keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                    
                    # Try to extract results
                    results = []
                    if "matches" in data:
                        results = data["matches"]
                    elif "results" in data:
                        results = data["results"]
                    elif isinstance(data, list):
                        results = data
                    
                    print(f"    Found {len(results)} results")
                    print(f"  ✅ {format_config['name']} - Success")
                    return True
                    
            except Exception as e:
                print(f"  ❌ {format_config['name']} - Error: {e}")
        
        print("❌ Vector search failed")
        return False
    
    def run_full_test(self, collection_name: str = "test_collection"):
        """Run complete API test suite."""
        print("🚀 Starting Endee API Test Suite")
        print("=" * 50)
        
        results = {
            "health_check": False,
            "create_collection": False,
            "insert_vector": False,
            "search_vectors": False
        }
        
        # Test 1: Health Check
        results["health_check"] = self.test_health_check()
        
        if not results["health_check"]:
            print("\n❌ Cannot proceed - Endee server not accessible")
            return results
        
        # Test 2: Create Collection
        results["create_collection"] = self.test_create_collection(collection_name)
        
        # Test 3: Insert Vector
        results["insert_vector"] = self.test_insert_vector(collection_name)
        
        # Test 4: Search Vectors (only if insert succeeded)
        if results["insert_vector"]:
            time.sleep(1)  # Give time for indexing
            results["search_vectors"] = self.test_search_vectors(collection_name)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Endee API is fully functional.")
        elif passed_tests > 0:
            print("⚠️  Partial functionality - some endpoints work.")
        else:
            print("❌ No endpoints working - check Endee configuration.")
        
        return results

def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Endee Vector Database API")
    parser.add_argument("--url", default="http://localhost:8080", 
                       help="Endee server URL")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--collection", default="test_collection",
                       help="Collection name for testing")
    
    args = parser.parse_args()
    
    tester = EndeeAPITester(args.url, args.api_key)
    results = tester.run_full_test(args.collection)
    
    # Exit with error code if tests failed
    if not any(results.values()):
        exit(1)

if __name__ == "__main__":
    main()