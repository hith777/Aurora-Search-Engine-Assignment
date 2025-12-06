from pydantic import BaseModel, Field
from typing import List, Optional


class MessageItem(BaseModel):
    """Individual message item from the API response."""
    id: str
    user_id: str
    user_name: str
    timestamp: str
    message: str


class MessagesResponse(BaseModel):
    """Response structure from the /messages endpoint."""
    total: int
    items: List[MessageItem]


class SearchRequest(BaseModel):
    """Request model for search endpoint."""
    query: str = Field(..., description="Search query to match against message content and user_name")
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    size: int = Field(10, ge=1, le=100, description="Number of results per page (max 100)")


class SearchResponse(BaseModel):
    """Response structure for the /search endpoint."""
    total: int
    items: List[MessageItem]
    page: int
    size: int
    total_pages: int
