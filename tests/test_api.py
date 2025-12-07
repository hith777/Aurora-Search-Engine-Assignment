#!/usr/bin/env python3
"""
Test script for Aurora Search Engine API.
Run this after starting the server: uvicorn app.main:app --reload
"""
import httpx
import json
import sys
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_response(title: str, response: httpx.Response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)


def test_health_check(client: httpx.Client):
    """Test the health check endpoint."""
    print_response("1. Health Check (GET /)", client.get(f"{BASE_URL}/"))


def test_reindex(client: httpx.Client):
    """Test the reindex endpoint."""
    print_response("2. Reindex (POST /reindex)", client.post(f"{BASE_URL}/reindex"))


def test_search(client: httpx.Client, query: str, page: int = 1, size: int = 10):
    """Test the search endpoint."""
    params = {"query": query, "page": page, "size": size}
    print_response(
        f"3. Search (GET /search?query={query}&page={page}&size={size})",
        client.get(f"{BASE_URL}/search", params=params)
    )


def test_search_pagination(client: httpx.Client):
    """Test search with different pagination."""
    query = "test"
    print_response(
        f"4. Search Page 1 (GET /search?query={query}&page=1&size=5)",
        client.get(f"{BASE_URL}/search", params={"query": query, "page": 1, "size": 5})
    )
    print_response(
        f"5. Search Page 2 (GET /search?query={query}&page=2&size=5)",
        client.get(f"{BASE_URL}/search", params={"query": query, "page": 2, "size": 5})
    )


def test_empty_query(client: httpx.Client):
    """Test search with empty query (should fail)."""
    print_response(
        "6. Empty Query (should return 422)",
        client.get(f"{BASE_URL}/search", params={"query": ""}, follow_redirects=True)
    )


def test_performance(client: httpx.Client, query: str):
    """Test search performance."""
    import time
    start = time.time()
    response = client.get(f"{BASE_URL}/search", params={"query": query})
    elapsed = (time.time() - start) * 1000  # Convert to milliseconds
    
    print(f"\n{'='*60}")
    print(f"7. Performance Test (query: '{query}')")
    print(f"{'='*60}")
    print(f"Response time: {elapsed:.2f}ms")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total results: {data.get('total', 0)}")
        print(f"Results returned: {len(data.get('items', []))}")
        if elapsed > 100:
            print("⚠️  WARNING: Response time exceeds 100ms requirement!")
        else:
            print("✅ Response time meets <100ms requirement")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Aurora Search Engine API Test Suite")
    print("="*60)
    print("\nMake sure the server is running:")
    print("  uvicorn app.main:app --reload\n")
    
    try:
        with httpx.Client(timeout=30.0) as client:
            # Basic tests
            test_health_check(client)
            test_reindex(client)
            
            # Search tests
            test_search(client, "hello")
            test_search(client, "test")
            test_search_pagination(client)
            
            # Performance test
            test_performance(client, "hello")
            
            # Error handling
            try:
                test_empty_query(client)
            except httpx.HTTPStatusError:
                print("\n✅ Empty query correctly rejected (422)")
            
            print("\n" + "="*60)
            print("All tests completed!")
            print("="*60 + "\n")
            
    except httpx.ConnectError:
        print("\n❌ ERROR: Could not connect to the server.")
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --reload\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
