"""
Basic usage example for the AI-Powered Support Assistant.
This example demonstrates how to use the support assistant programmatically.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.support_assistant import SupportAssistant

async def main():
    """Demonstrate basic usage of the support assistant."""
    
    # Initialize the support assistant
    assistant = SupportAssistant()
    
    print("Initializing AI Support Assistant...")
    success = assistant.initialize()
    
    if not success:
        print("Failed to initialize the assistant")
        return
    
    print("Assistant initialized successfully!\n")
    
    # Example queries
    test_queries = [
        "I can't log into my account",
        "My payment was declined",
        "The app keeps crashing",
        "Website is loading very slowly",
        "I'm not getting email notifications"
    ]
    
    print("Testing support queries:\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        
        # Handle the query
        result = assistant.handle_query(query)
        
        print(f"Action: {result['action']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Response: {result['response']}")
        print(f"Similar tickets found: {len(result['similar_tickets'])}")
        
        if result['similar_tickets']:
            print("Most similar ticket:")
            top_ticket = result['similar_tickets'][0]
            metadata = top_ticket.get('metadata', {})
            print(f"  - Title: {metadata.get('title', 'N/A')}")
            print(f"  - Similarity: {top_ticket.get('score', 0):.3f}")
        
        print("-" * 50)
    
    # Add a new ticket example
    print("\nAdding a new support ticket...")
    
    new_ticket = {
        "title": "Cannot access premium features",
        "description": "User has paid for premium subscription but cannot access premium features",
        "category": "billing",
        "status": "open",
        "priority": "high"
    }
    
    success = assistant.add_ticket(new_ticket)
    print(f"Ticket added successfully: {success}")
    
    # Test query against the new ticket
    print("\nTesting query against newly added ticket:")
    result = assistant.handle_query("I paid for premium but can't use premium features")
    print(f"Action: {result['action']}")
    print(f"Response: {result['response']}")

if __name__ == "__main__":
    asyncio.run(main())