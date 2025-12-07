#!/usr/bin/env python3
"""
Performance testing script for Aurora Search Engine API.
Tests response times and verifies <100ms requirement.
"""
import httpx
import time
import statistics
from typing import List, Dict
import sys


BASE_URL = "http://localhost:8000"  # Default, can be overridden with --url flag


def measure_response_time(client: httpx.Client, base_url: str, endpoint: str, params: Dict = None) -> float:
    """
    Measure the response time for an API call.
    
    Returns:
        Response time in milliseconds
    """
    start = time.perf_counter()
    try:
        url = f"{base_url}{endpoint}" if not endpoint.startswith("http") else endpoint
        response = client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to milliseconds
        return elapsed, response
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return elapsed, None


def test_search_performance(client: httpx.Client, base_url: str, query: str, iterations: int = 10) -> Dict:
    """
    Test search performance with multiple iterations.
    
    Returns:
        Dictionary with performance statistics
    """
    times = []
    errors = 0
    
    print(f"\nTesting search query: '{query}'")
    print(f"Running {iterations} iterations...")
    
    for i in range(iterations):
        elapsed, response = measure_response_time(
            client,
            base_url,
            "/search",
            params={"query": query}
        )
        times.append(elapsed)
        
        if response is None:
            errors += 1
        elif response.status_code != 200:
            errors += 1
        
        # Progress indicator
        if (i + 1) % 5 == 0:
            print(f"  Completed {i + 1}/{iterations} requests...")
    
    if not times:
        return {"error": "All requests failed"}
    
    return {
        "query": query,
        "iterations": iterations,
        "errors": errors,
        "times": times,
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "p95": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0],
        "p99": sorted(times)[int(len(times) * 0.99)] if len(times) > 1 else times[0],
    }


def print_performance_stats(stats: Dict):
    """Print performance statistics in a readable format."""
    if "error" in stats:
        print(f"❌ Error: {stats['error']}")
        return
    
    print("\n" + "="*70)
    print("PERFORMANCE STATISTICS")
    print("="*70)
    print(f"Query: '{stats['query']}'")
    print(f"Iterations: {stats['iterations']}")
    print(f"Errors: {stats['errors']}")
    print("-"*70)
    print(f"Mean (Average):     {stats['mean']:8.2f} ms")
    print(f"Median:             {stats['median']:8.2f} ms")
    print(f"Min:                 {stats['min']:8.2f} ms")
    print(f"Max:                 {stats['max']:8.2f} ms")
    print(f"Standard Deviation:  {stats['stdev']:8.2f} ms")
    print(f"95th Percentile:     {stats['p95']:8.2f} ms")
    print(f"99th Percentile:     {stats['p99']:8.2f} ms")
    print("="*70)
    
    # Check against requirements
    mean = stats['mean']
    p95 = stats['p95']
    
    print("\n📊 REQUIREMENT CHECK:")
    if mean < 100:
        print(f"✅ Mean response time ({mean:.2f}ms) meets <100ms requirement")
    else:
        print(f"❌ Mean response time ({mean:.2f}ms) exceeds 100ms requirement")
    
    if p95 < 100:
        print(f"✅ 95th percentile ({p95:.2f}ms) meets <100ms requirement")
    else:
        print(f"⚠️  95th percentile ({p95:.2f}ms) exceeds 100ms requirement")
    
    # Bonus goal check
    if mean < 30:
        print(f"🎯 BONUS: Mean response time ({mean:.2f}ms) meets 30ms target!")
    else:
        print(f"💡 To reach 30ms: Consider implementing optimizations from README.md")


def test_multiple_queries(client: httpx.Client, base_url: str, queries: List[str], iterations: int = 10):
    """Test performance with multiple different queries."""
    print("\n" + "="*70)
    print("MULTI-QUERY PERFORMANCE TEST")
    print("="*70)
    
    all_stats = []
    for query in queries:
        stats = test_search_performance(client, base_url, query, iterations)
        all_stats.append(stats)
        print_performance_stats(stats)
    
    # Summary
    if all_stats:
        print("\n" + "="*70)
        print("OVERALL SUMMARY")
        print("="*70)
        overall_mean = statistics.mean([s['mean'] for s in all_stats if 'mean' in s])
        overall_p95 = statistics.mean([s['p95'] for s in all_stats if 'p95' in s])
        
        print(f"Average mean across all queries: {overall_mean:.2f} ms")
        print(f"Average 95th percentile:         {overall_p95:.2f} ms")
        
        if overall_mean < 100:
            print("✅ Overall performance meets <100ms requirement")
        else:
            print("❌ Overall performance exceeds 100ms requirement")


def quick_test(client: httpx.Client, base_url: str, query: str = "hello"):
    """Quick single-request test."""
    print(f"\nQuick performance test for query: '{query}'")
    elapsed, response = measure_response_time(
        client,
        base_url,
        "/search",
        params={"query": query}
    )
    
    print(f"\nResponse time: {elapsed:.2f} ms")
    
    if response:
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Total results: {data.get('total', 0)}")
        print(f"Results returned: {len(data.get('items', []))}")
    
    if elapsed < 100:
        print("✅ Meets <100ms requirement")
    else:
        print("❌ Exceeds 100ms requirement")
    
    if elapsed < 30:
        print("🎯 Meets 30ms bonus target!")
    else:
        print(f"💡 {elapsed - 30:.2f}ms away from 30ms target")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Aurora Search Engine API performance")
    parser.add_argument("--query", "-q", default="hello", help="Search query to test")
    parser.add_argument("--iterations", "-n", type=int, default=10, help="Number of iterations")
    parser.add_argument("--quick", action="store_true", help="Run quick single-request test")
    parser.add_argument("--multi", action="store_true", help="Test multiple queries")
    parser.add_argument("--url", "-u", default=None, help="Base URL of the API (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    # Use provided URL or default
    base_url = args.url if args.url else BASE_URL
    
    print("="*70)
    print("Aurora Search Engine - Performance Test")
    print("="*70)
    print(f"Testing API at: {base_url}")
    
    if not args.url:
        print("\n💡 Tip: Use --url to test a deployed instance:")
        print("   python test_performance.py --url https://your-app.onrender.com")
    
    try:
        with httpx.Client(timeout=30.0) as client:
            # Test connection first
            try:
                response = client.get(f"{base_url}/")
                response.raise_for_status()
            except Exception as e:
                print(f"\n❌ ERROR: Could not connect to server at {base_url}")
                print(f"   Error: {e}")
                if not args.url:
                    print("\nMake sure the server is running:")
                    print("  uvicorn app.main:app --reload")
                sys.exit(1)
            
            if args.quick:
                quick_test(client, base_url, args.query)
            elif args.multi:
                queries = ["hello", "test", "message", "user", "the"]
                test_multiple_queries(client, base_url, queries, args.iterations)
            else:
                stats = test_search_performance(client, base_url, args.query, args.iterations)
                print_performance_stats(stats)
                
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
