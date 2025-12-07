#!/bin/bash

# Quick script to test deployed API speed
# Usage: ./test_deployed.sh https://your-app.onrender.com

API_URL="${1:-http://localhost:8000}"
QUERY="${2:-hello}"

echo "=========================================="
echo "Testing: $API_URL"
echo "Query: $QUERY"
echo "=========================================="
echo ""

# Single test with detailed timing
echo "Single Request Test:"
echo "URL: $API_URL/search?query=$QUERY"
echo ""

START=$(date +%s%N)
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}\nTIME_TOTAL:%{time_total}\nTIME_CONNECT:%{time_connect}\nTIME_STARTTRANSFER:%{time_starttransfer}" \
    "$API_URL/search?query=$QUERY")
END=$(date +%s%N)

# Extract timing info
TIME_TOTAL=$(echo "$RESPONSE" | grep "TIME_TOTAL:" | cut -d: -f2)
TIME_CONNECT=$(echo "$RESPONSE" | grep "TIME_CONNECT:" | cut -d: -f2)
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)

# Calculate in milliseconds
TIME_MS=$(echo "$TIME_TOTAL * 1000" | bc -l | xargs printf "%.2f")
CONNECT_MS=$(echo "$TIME_CONNECT * 1000" | bc -l | xargs printf "%.2f")

echo "Response Time: ${TIME_MS} ms"
echo "Connection Time: ${CONNECT_MS} ms"
echo "HTTP Status: $HTTP_CODE"
echo ""

# Check requirement
if (( $(echo "$TIME_MS < 100" | bc -l) )); then
    echo "✅ Meets <100ms requirement"
else
    echo "❌ Exceeds 100ms requirement"
fi

if (( $(echo "$TIME_MS < 30" | bc -l) )); then
    echo "🎯 BONUS: Meets 30ms target!"
fi

echo ""
echo "Full URL tested:"
echo "$API_URL/search?query=$QUERY"
