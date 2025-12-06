"""
In-memory indexing service for fast message search.
Indexes messages by content and user_name for efficient searching.
"""
from typing import List, Dict, Tuple
from app.models import MessageItem, SearchResponse


class Indexer:
    """In-memory search index for messages."""
    
    def __init__(self):
        self.messages: List[MessageItem] = []
        # Pre-processed lowercase searchable text: (message_lower, user_name_lower)
        self.searchable_text: List[Tuple[str, str]] = []
        self.indexed: bool = False
    
    def index_messages(self, messages: List[MessageItem]):
        """
        Index a list of messages for fast searching.
        Pre-processes searchable text to avoid repeated lowercasing during search.
        
        Args:
            messages: List of MessageItem objects to index
        """
        # Store messages
        self.messages = messages
        
        # Pre-process searchable text (lowercase) for faster search
        # This avoids calling .lower() on every search
        self.searchable_text = [
            (msg.message.lower(), msg.user_name.lower())
            for msg in messages
        ]
        
        # Optionally sort by timestamp if required
        # self.messages.sort(key=lambda x: x.timestamp)
        
        self.indexed = True
    
    def search(self, query: str, page: int = 1, size: int = 10) -> SearchResponse:
        """
        Search messages by query string.
        Searches in message content and user_name fields (case-insensitive).
        Optimized with pre-processed lowercase text.
        
        Args:
            query: Search query string
            page: Page number (1-indexed)
            size: Number of results per page
            
        Returns:
            SearchResponse with paginated results
        """
        if not self.indexed or not self.messages:
            return SearchResponse(
                total=0,
                items=[],
                page=page,
                size=size,
                total_pages=0
            )
        
        query_lower = query.lower().strip()
        
        # Filter messages that match the query using pre-processed text
        # Search in both message content and user_name
        matching_messages = [
            self.messages[i] for i in range(len(self.messages))
            if query_lower in self.searchable_text[i][0] or query_lower in self.searchable_text[i][1]
        ]
        
        total = len(matching_messages)
        
        # Calculate pagination
        total_pages = (total + size - 1) // size if total > 0 else 0
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        
        # Get paginated results
        paginated_items = matching_messages[start_idx:end_idx]
        
        return SearchResponse(
            total=total,
            items=paginated_items,
            page=page,
            size=size,
            total_pages=total_pages
        )
    
    def get_stats(self) -> Dict:
        """Get indexing statistics."""
        return {
            "indexed": self.indexed,
            "message_count": len(self.messages)
        }
    
    def get_all_messages(self, page: int = 1, size: int = 100) -> List[MessageItem]:
        """
        Get all indexed messages with pagination.
        
        Args:
            page: Page number (1-indexed)
            size: Number of results per page
            
        Returns:
            List of MessageItem objects
        """
        if not self.indexed or not self.messages:
            return []
        
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        
        return self.messages[start_idx:end_idx]
