#!/usr/bin/env python3
"""
Script to fetch and display all messages from the /messages API.
"""
import httpx
import json
from typing import List
from app.models import MessageItem, MessagesResponse


BASE_URL = "https://november7-730026606190.europe-west1.run.app"


async def fetch_all_messages():
    """Fetch all messages from the API."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # Try with trailing slash first
        url = f"{BASE_URL}/messages/"
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            messages_response = MessagesResponse(**data)
            return messages_response.items
            
        except Exception as e:
            print(f"Error fetching messages: {e}")
            # Try without trailing slash
            url = f"{BASE_URL}/messages"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            messages_response = MessagesResponse(**data)
            return messages_response.items


def display_messages(messages: List[MessageItem], limit: int = None):
    """Display messages in a readable format."""
    total = len(messages)
    display_count = limit if limit else total
    
    print(f"\n{'='*80}")
    print(f"Total Messages: {total}")
    if limit:
        print(f"Displaying first {display_count} messages")
    print(f"{'='*80}\n")
    
    for i, msg in enumerate(messages[:display_count], 1):
        print(f"Message {i}:")
        print(f"  ID: {msg.id}")
        print(f"  User ID: {msg.user_id}")
        print(f"  User Name: {msg.user_name}")
        print(f"  Timestamp: {msg.timestamp}")
        print(f"  Message: {msg.message[:100]}{'...' if len(msg.message) > 100 else ''}")
        print("-" * 80)


def save_messages_to_file(messages: List[MessageItem], filename: str = "messages.json"):
    """Save messages to a JSON file."""
    messages_dict = [msg.model_dump() for msg in messages]
    with open(filename, 'w') as f:
        json.dump(messages_dict, f, indent=2)
    print(f"\n✅ Saved {len(messages)} messages to {filename}")


async def main():
    """Main function."""
    import asyncio
    
    print("Fetching messages from the API...")
    print(f"URL: {BASE_URL}/messages/")
    
    try:
        messages = await fetch_all_messages()
        
        if not messages:
            print("No messages found.")
            return
        
        # Display first 10 messages
        display_messages(messages, limit=10)
        
        # Ask if user wants to see all or save to file
        print(f"\nTotal messages: {len(messages)}")
        print("\nOptions:")
        print("1. Display all messages")
        print("2. Save all messages to JSON file")
        print("3. Display more messages (specify count)")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            display_messages(messages)
        elif choice == "2":
            filename = input("Enter filename (default: messages.json): ").strip() or "messages.json"
            save_messages_to_file(messages, filename)
        elif choice == "3":
            try:
                count = int(input("How many messages to display? "))
                display_messages(messages, limit=count)
            except ValueError:
                print("Invalid number")
        else:
            print("Exiting...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
