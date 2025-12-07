#!/bin/bash

# Test script for Aurora Search Engine API
# Make sure the server is running: uvicorn app.main:app --reload

BASE_URL="http://localhost:8000"

echo "=== Testing Aurora Search Engine API ==="
echo ""

# Test 1: Health check
echo "1. Testing health check endpoint (GET /)..."
curl -s "$BASE_URL/" | python3 -m json.tool
echo -e "\n"

# Test 2: Reindex (if needed)
echo "2. Testing reindex endpoint (POST /reindex)..."
curl -s -X POST "$BASE_URL/reindex" | python3 -m json.tool
echo -e "\n"

# Test 3: Search with a simple query
echo "3. Testing search endpoint (GET /search?query=hello)..."
curl -s "$BASE_URL/search?query=hello" | python3 -m json.tool
echo -e "\n"

# Test 4: Search with pagination
echo "4. Testing search with pagination (GET /search?query=test&page=1&size=5)..."
curl -s "$BASE_URL/search?query=test&page=1&size=5" | python3 -m json.tool
echo -e "\n"

# Test 5: Search for user name
echo "5. Testing search for user name (GET /search?query=john)..."
curl -s "$BASE_URL/search?query=john" | python3 -m json.tool
echo -e "\n"

# Test 6: Empty query (should fail)
echo "6. Testing empty query (should return 422)..."
curl -s "$BASE_URL/search?query=" | python3 -m json.tool
echo -e "\n"

echo "=== Testing complete ==="
