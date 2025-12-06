from fastapi import FastAPI, HTTPException, Query, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uvicorn

from app.models import SearchResponse
from app.services.data_fetcher import DataFetcher
from app.services.indexer import Indexer

app = FastAPI(
    title="Aurora Search Engine",
    description="A simple search engine for messages",
    version="1.0.0"
)


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to add response time to headers."""
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
        response.headers["X-Response-Time"] = f"{process_time:.2f}ms"
        return response


app.add_middleware(TimingMiddleware)

# Initialize services
data_fetcher = DataFetcher()
indexer = Indexer()


async def perform_reindex():
    """Internal function to perform reindexing."""
    messages = await data_fetcher.fetch_all_messages()
    indexer.index_messages(messages)
    return len(messages)


@app.on_event("startup")
async def startup_event():
    """Initialize the search index on startup."""
    try:
        count = await perform_reindex()
        print(f"Indexed {count} messages on startup")
    except Exception as e:
        print(f"Warning: Failed to index messages on startup: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Aurora Search Engine"}


@app.post("/reindex")
async def reindex():
    """Manually trigger reindexing of messages."""
    try:
        count = await perform_reindex()
        return {"status": "success", "message": f"Indexed {count} messages"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")


@app.get("/messages")
async def get_messages(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(100, ge=1, le=1000, description="Number of results per page")
):
    """
    Get all indexed messages with pagination.
    Useful for viewing all messages in the index.
    """
    messages = indexer.get_all_messages(page, size)
    total = len(indexer.messages) if indexer.indexed else 0
    total_pages = (total + size - 1) // size if total > 0 else 0
    
    return {
        "total": total,
        "items": messages,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }


@app.get("/search")
async def search(
    request: Request,
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(10, ge=1, le=100, description="Number of results per page")
):
    """
    Search messages by query string.
    
    Searches in message content and user_name fields.
    Returns paginated results with response time included.
    
    Response includes:
    - search_time_ms: Time taken for the search operation only
    - total_time_ms: Total request processing time (more accurate)
    - meets_requirement: true if total_time < 100ms
    - meets_bonus_target: true if total_time < 30ms
    """
    if not query or not query.strip():
        raise HTTPException(status_code=422, detail="Query parameter is required")
    
    # Measure total request time from start
    request_start = time.perf_counter()
    
    # Measure search operation time
    search_start = time.perf_counter()
    results = indexer.search(query.strip(), page, size)
    search_time = (time.perf_counter() - search_start) * 1000  # Convert to milliseconds
    
    # Convert SearchResponse to dict and add timing info
    result_dict = results.model_dump()
    
    # Calculate total time (up to this point, before serialization)
    total_time = (time.perf_counter() - request_start) * 1000
    
    # Add timing information
    result_dict["search_time_ms"] = round(search_time, 3)
    result_dict["total_time_ms"] = round(total_time, 3)
    result_dict["meets_requirement"] = total_time < 100
    result_dict["meets_bonus_target"] = total_time < 30
    
    # Also add performance note
    if total_time < 30:
        result_dict["performance_note"] = "🎯 Excellent! Meets 30ms bonus target"
    elif total_time < 100:
        result_dict["performance_note"] = "✅ Good! Meets <100ms requirement"
    else:
        result_dict["performance_note"] = f"⚠️ Exceeds 100ms requirement by {total_time - 100:.2f}ms"
    
    return result_dict


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)