#!/usr/bin/env python3
"""
Simple script to quickly view all messages from the API.
Usage: python view_messages_simple.py
"""
import httpx
import json
import asyncio
from app.models import MessagesResponse


BASE_URL = "https://november7-730026606190.europe-west1.run.app"


async def main():
    """Fetch and display all messages."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        url = f"{BASE_URL}/messages/"
        
        print(f"Fetching messages from {url}...")
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            messages_response = MessagesResponse(**data)
            messages = messages_response.items
            
            print(f"\n✅ Successfully fetched {len(messages)} messages")
            print(f"Total in API response: {messages_response.total}\n")
            
            # Display summary
            print("=" * 80)
            print("MESSAGE SUMMARY")
            print("=" * 80)
            
            for i, msg in enumerate(messages[:20], 1):  # Show first 20
                print(f"\n[{i}] {msg.user_name} ({msg.user_id})")
                print(f"    Time: {msg.timestamp}")
                print(f"    Message: {msg.message[:150]}{'...' if len(msg.message) > 150 else ''}")
            
            if len(messages) > 20:
                print(f"\n... and {len(messages) - 20} more messages")
            
            # Save to file
            print("\n" + "=" * 80)
            save = input("Save all messages to messages.json? (y/n): ").strip().lower()
            if save == 'y':
                messages_dict = [msg.model_dump() for msg in messages]
                with open("messages.json", 'w') as f:
                    json.dump({
                        "total": len(messages),
                        "items": messages_dict
                    }, f, indent=2)
                print("✅ Saved to messages.json")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
