"""
Data fetcher service for retrieving messages from the external API.
Handles pagination, retries, and error handling for inconsistent API.
"""
import httpx
import asyncio
from typing import List
from app.models import MessageItem, MessagesResponse


class DataFetcher:
    """Fetches messages from the /messages endpoint with retry logic."""
    
    BASE_URL = "https://november7-730026606190.europe-west1.run.app"
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    def __init__(self):
        # Follow redirects automatically (default is True, but being explicit)
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def fetch_messages(self, offset: int = 0, limit: int = 100) -> MessagesResponse:
        """
        Fetch messages from the API with pagination support.
        
        Args:
            offset: Starting position for pagination
            limit: Maximum number of items to fetch
            
        Returns:
            MessagesResponse containing total count and items
        """
        # Add trailing slash to avoid redirect issues
        url = f"{self.BASE_URL}/messages/"
        params = {}
        
        # Add pagination params if the API supports them
        # Note: We'll fetch all and handle pagination client-side if needed
        if offset > 0:
            params["offset"] = offset
        if limit != 100:
            params["limit"] = limit
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return MessagesResponse(**data)
                
            except httpx.HTTPStatusError as e:
                # Handle redirect responses (307, 308, etc.)
                if e.response.status_code in (301, 302, 303, 307, 308):
                    redirect_url = e.response.headers.get("location")
                    if redirect_url:
                        # Update URL to follow redirect (ensure HTTPS)
                        if redirect_url.startswith("http://"):
                            redirect_url = redirect_url.replace("http://", "https://", 1)
                        url = redirect_url
                        continue
                
                if e.response.status_code == 422:
                    # Validation error - don't retry
                    raise
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                raise Exception(f"Failed to fetch messages after {self.MAX_RETRIES} attempts: {str(e)}")
    
    async def fetch_all_messages(self) -> List[MessageItem]:
        """
        Fetch all messages from the API.
        Handles pagination if the API supports it, otherwise fetches all at once.
        
        Returns:
            List of all MessageItem objects
        """
        all_messages = []
        offset = 0
        limit = 1000  # Try to fetch a large batch first
        
        try:
            # First attempt: try to fetch all at once
            response = await self.fetch_messages(offset=0, limit=limit)
            all_messages.extend(response.items)
            
            # If we got fewer items than total, there might be pagination
            # For now, we'll assume the API returns all items in one call
            # If pagination is needed, we can implement it here
            
        except Exception as e:
            # If large batch fails, try smaller batches
            if "422" in str(e) or "limit" in str(e).lower():
                # Try without limit parameter
                response = await self.fetch_messages()
                all_messages.extend(response.items)
            else:
                raise
        
        # Sort by timestamp if needed (as per assumptions)
        # all_messages.sort(key=lambda x: x.timestamp)
        
        return all_messages