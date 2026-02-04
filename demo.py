#!/usr/bin/env python3
"""
Quick demo script for the AI Support Assistant.
Run this to see the system in action without any setup.
"""

import asyncio
from src.support_assistant import SupportAssistant

def main():
    """Run a quick demo of the support assistant."""
    print("🤖 AI Support Assistant Demo")
    print("=" * 40)
    
    # Initialize assistant
    print("Initializing system...")
    assistant = SupportAssistant()
    assistant.initialize()
    
    print("✅ System ready!\n")
    
    # Demo queries
    demo_queries = [
        "I can't login to my account",
        "My payment was declined", 
        "The app keeps crashing",
        "Website is very slow",
        "Not receiving email notifications"
    ]
    
    print("🔍 Testing support queries:\n")
    
    for i, query in enumerate(demo_queries, 1):
        print(f"Query {i}: '{query}'")
        
        result = assistant.handle_query(query)
        
        print(f"  Action: {result['action'].upper()}")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Response: {result['response']}")
        
        if result['similar_tickets']:
            print(f"  Similar tickets found: {len(result['similar_tickets'])}")
        
        print()
    
    print("🎉 Demo completed!")
    print("Start the full API server with: python main.py")
    print("Then visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()