#!/usr/bin/env python3

import requests
import sys
from datetime import datetime
import json

def format_chat_history(chat_id, access_token):
    """Fetch and beautifully format chat history"""
    
    # API call
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"http://127.0.0.1:8000/chat/history/{chat_id}", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    messages = data["messages"]
    
    print("=" * 80)
    print(f"💬 CHAT HISTORY - Chat ID: {chat_id}")
    print("=" * 80)
    print()
    
    for msg in messages:
        # Parse timestamp
        timestamp = datetime.fromisoformat(msg["timestamp"].replace('Z', '+00:00'))
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Format based on sender
        if msg["sender"] == "user":
            print(f"👤 USER ({time_str}):")
            print(f"   {msg['content']}")
        else:
            print(f"🧠 EINSTEIN ({time_str}):")
            # Word wrap for long AI responses
            words = msg['content'].split()
            lines = []
            current_line = "   "
            
            for word in words:
                if len(current_line + word) > 75:
                    lines.append(current_line)
                    current_line = "   " + word
                else:
                    current_line += " " + word if current_line != "   " else word
            
            if current_line.strip():
                lines.append(current_line)
            
            for line in lines:
                print(line)
        
        print()
        print("-" * 80)
        print()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python view_chat.py <chat_id> <access_token>")
        print("Example: python view_chat.py 1 eyJhbGciOiJIUzI1NiIs...")
        sys.exit(1)
    
    chat_id = sys.argv[1]
    access_token = sys.argv[2]
    
    format_chat_history(chat_id, access_token) 