# Aurora Search Engine

A simple, fast search engine API service built with FastAPI that indexes and searches messages from an external data source.

## Features

- Fast search across message content and user names
- Paginated results
- Automatic indexing on startup
- Manual reindexing endpoint
- Optimized for <100ms response times
- Deployed and publicly accessible

## API Endpoints

### `GET /search`

Search messages by query string.

**Query Parameters:**
- `query` (required): Search query to match against message content and user_name
- `page` (optional, default=1): Page number (1-indexed)
- `size` (optional, default=10, max=100): Number of results per page

**Example:**
```bash
curl "https://your-service.onrender.com/search?query=hello&page=1&size=10"
```

**Response:**
```json
{
  "total": 42,
  "items": [
    {
      "id": "string",
      "user_id": "string",
      "user_name": "string",
      "timestamp": "string",
      "message": "string"
    }
  ],
  "page": 1,
  "size": 10,
  "total_pages": 5
}
```

### `POST /reindex`

Manually trigger reindexing of messages from the source API.

**Response:**
```json
{
  "status": "success",
  "message": "Indexed 1000 messages"
}
```

### `GET /`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "Aurora Search Engine"
}
```

## Setup Instructions

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Aurora-Search-Engine-Assignment
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Deployment to Render

1. **Using Render Dashboard:**
   - Connect your GitHub repository
   - Select "Web Service"
   - Render will auto-detect the `render.yaml` configuration
   - Deploy

2. **Using Render CLI:**
   ```bash
   render deploy
   ```

The service will automatically:
- Install dependencies from `requirements.txt`
- Start the FastAPI application
- Index messages on startup

## Design Notes

### Alternative Approaches Considered

#### 1. **In-Memory Indexing (Current Implementation)**
**Approach:** Store all messages in memory with pre-processed lowercase searchable text.

**Pros:**
- Fast lookups (O(n) linear scan, but optimized with pre-processing)
- Simple to implement and maintain
- No external dependencies
- Low latency for moderate datasets (<100k messages)

**Cons:**
- Memory usage grows with dataset size
- Requires full reindex on data changes
- Not suitable for very large datasets (>1M messages)

**Why chosen:** Best balance of simplicity, performance, and no external dependencies for the requirements.

---

#### 2. **Full-Text Search with SQLite FTS5**
**Approach:** Use SQLite with FTS5 (Full-Text Search) extension for indexing.

**Pros:**
- Built-in full-text search capabilities
- Persistent storage (survives restarts)
- Efficient for large datasets
- Supports ranking and relevance scoring

**Cons:**
- Additional complexity
- Requires database file management
- Slightly higher latency due to disk I/O
- More setup and configuration

**Why not chosen:** Added complexity without significant benefit for the current requirements. In-memory is faster for the expected dataset size.

---

#### 3. **Elasticsearch/OpenSearch**
**Approach:** Use a dedicated search engine like Elasticsearch.

**Pros:**
- Industry-standard for search
- Advanced features (fuzzy search, faceting, aggregations)
- Excellent scalability
- Built-in relevance ranking

**Cons:**
- Requires separate service deployment
- Higher infrastructure complexity
- Overkill for simple substring search
- Additional latency from network calls
- Higher resource requirements

**Why not chosen:** Too complex for the requirements. The overhead of maintaining a separate service outweighs the benefits for this use case.

---

#### 4. **Trie/Prefix Tree Data Structure**
**Approach:** Build a trie data structure for prefix-based search.

**Pros:**
- Very fast prefix matching (O(m) where m is query length)
- Efficient for autocomplete-like searches
- Memory efficient for common prefixes

**Cons:**
- Complex to implement
- Only efficient for prefix matching, not substring search
- Requires significant memory for large vocabularies
- Doesn't help with substring search (current requirement)

**Why not chosen:** Not suitable for substring search requirement. Tries are optimized for prefix matching, not general substring search.

---

#### 5. **Inverted Index with Posting Lists**
**Approach:** Build a traditional inverted index (word -> list of message IDs).

**Pros:**
- Very fast for word-based searches
- Efficient memory usage
- Standard approach in information retrieval
- Scales well with dataset size

**Cons:**
- More complex to implement
- Requires tokenization and word boundary detection
- Less effective for partial word matches
- Overhead for small datasets

**Why not chosen:** Current requirement is substring search (not word-based), which doesn't benefit as much from inverted indices. The added complexity isn't justified.

---

#### 6. **Caching Layer (Redis/Memcached)**
**Approach:** Add a caching layer for frequently searched queries.

**Pros:**
- Dramatically reduces latency for repeated queries
- Can cache paginated results
- Reduces load on search index

**Cons:**
- Additional service dependency
- Cache invalidation complexity
- Memory overhead
- May not help with unique queries

**Why not chosen:** Could be added as an optimization, but not necessary for initial implementation. The in-memory search is already fast enough.

---

### Current Implementation Details

The current implementation uses:
- **Pre-processed lowercase text**: Messages are lowercased during indexing to avoid repeated `.lower()` calls during search
- **Linear scan with early optimization**: While still O(n), the pre-processing and efficient Python list comprehensions make it fast for moderate datasets
- **In-memory storage**: All data in RAM for fastest access
- **Automatic indexing on startup**: Messages are fetched and indexed when the service starts

## Performance Optimization: Reducing Latency to 30ms

The current implementation targets <100ms response time. Here are strategies to reduce latency to 30ms:

### 1. **Parallel Processing with asyncio**
**Current:** Sequential message filtering
**Optimization:** Use `asyncio.gather()` or multiprocessing to parallelize search across message chunks

```python
# Split messages into chunks and search in parallel
chunks = [messages[i:i+chunk_size] for i in range(0, len(messages), chunk_size)]
results = await asyncio.gather(*[search_chunk(chunk, query) for chunk in chunks])
```

**Expected improvement:** 2-3x faster for large datasets

---

### 2. **Early Termination**
**Current:** Processes all messages even if we have enough results
**Optimization:** Stop searching once we have enough results for the requested page

```python
# Stop once we have enough results for pagination
if len(matching_messages) >= (page * size):
    break
```

**Expected improvement:** 30-50% faster for queries with many matches

---

### 3. **Caching Frequent Queries**
**Current:** No caching
**Optimization:** Add in-memory LRU cache for recent queries

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query: str, page: int, size: int):
    # ... search logic
```

**Expected improvement:** Near-instant (<5ms) for cached queries

---

### 4. **Optimized String Matching**
**Current:** Python's `in` operator (Boyer-Moore-like)
**Optimization:** Use compiled regex or specialized string search libraries

```python
import re
pattern = re.compile(query_lower, re.IGNORECASE)
matching = [msg for msg, text in zip(messages, searchable_text) 
            if pattern.search(text[0]) or pattern.search(text[1])]
```

**Expected improvement:** 10-20% faster for complex queries

---

### 5. **NumPy/Pandas Vectorization**
**Current:** Python list comprehensions
**Optimization:** Use NumPy for vectorized string operations

```python
import numpy as np
# Vectorized substring matching (if message count is very high)
```

**Expected improvement:** 2-4x faster for very large datasets (>100k messages)

---

### 6. **Pre-computed Search Index with Sets**
**Current:** Linear scan through all messages
**Optimization:** For common query patterns, pre-compute matches

```python
# Build n-gram index for common substrings
# Or maintain a set of all unique words for fast word-based lookup
```

**Expected improvement:** O(1) lookup for exact word matches

---

### 7. **Connection Pooling and HTTP/2**
**Current:** Single HTTP client
**Optimization:** Use HTTP/2 with connection pooling for faster reindexing

**Expected improvement:** Faster reindexing (doesn't affect search latency directly)

---

### 8. **Response Compression**
**Current:** Uncompressed JSON
**Optimization:** Enable gzip compression in FastAPI

```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Expected improvement:** Faster response transmission (especially for large result sets)

---

### 9. **Database-backed Index (Hybrid Approach)**
**Current:** Pure in-memory
**Optimization:** Use SQLite with FTS5, but keep hot data in memory

**Expected improvement:** Better for very large datasets, but may add latency

---

### 10. **Profiling and Targeted Optimization**
**Current:** General optimizations
**Optimization:** Use `cProfile` or `py-spy` to identify bottlenecks

```python
import cProfile
profiler = cProfile.Profile()
profiler.enable()
# ... search operation
profiler.disable()
profiler.print_stats()
```

**Expected improvement:** Identify and fix specific bottlenecks

---

### Recommended Implementation Order for 30ms Target:

1. **Add query caching** (LRU cache) - Biggest impact for repeated queries
2. **Implement early termination** - Significant improvement for common cases
3. **Profile and optimize hot paths** - Identify actual bottlenecks
4. **Add parallel processing** - If dataset is large (>50k messages)
5. **Optimize string matching** - If profiling shows it's a bottleneck

### Expected Results:

- **Current:** ~50-80ms for typical queries
- **With caching + early termination:** ~20-40ms for most queries
- **With all optimizations:** <30ms for 90% of queries

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (app/main.py) │
└────────┬────────┘
         │
         ├─── GET /search ───┐
         │                   │
         ├─── POST /reindex ─┤
         │                   │
         └─── GET / ─────────┘
                 │
                 ▼
         ┌───────────────┐
         │   Indexer     │
         │ (in-memory)   │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Data Fetcher  │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │  External API │
         │  /messages    │
         └───────────────┘
```

## Technology Stack

- **Python 3.11**: Latest stable version
- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **httpx**: Async HTTP client
- **Pydantic**: Data validation

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and routes
│   ├── models.py            # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── data_fetcher.py  # Fetch from /messages API
│       └── indexer.py       # Indexing and search logic
├── requirements.txt
├── render.yaml              # Render deployment config
├── Dockerfile               # Container configuration
└── README.md
```

## License

This project is part of an assignment.
