from typing import List, Dict, Any
import random

class MockLLM:
    """Mock LLM for demo mode when OpenAI API key is not available."""
    
    def __init__(self):
        self.response_templates = {
            "authentication": {
                "action": "solution",
                "responses": [
                    "Try resetting your password using the 'Forgot Password' link on the login page.",
                    "Clear your browser cache and cookies, then try logging in again.",
                    "Make sure Caps Lock is off and check for any extra spaces in your credentials."
                ]
            },
            "billing": {
                "action": "solution", 
                "responses": [
                    "Please check if your payment method is still valid and has sufficient funds.",
                    "Try using a different payment method or contact your bank.",
                    "Verify that your billing address matches your payment method."
                ]
            },
            "technical": {
                "action": "solution",
                "responses": [
                    "Try refreshing the page or clearing your browser cache.",
                    "Update your app to the latest version from the app store.",
                    "Check your internet connection and try again."
                ]
            },
            "performance": {
                "action": "solution",
                "responses": [
                    "This might be a temporary server issue. Please try again in a few minutes.",
                    "Clear your browser cache and disable browser extensions to improve performance.",
                    "Try using a different browser or device to see if the issue persists."
                ]
            }
        }
    
    def generate_response(self, query: str, similar_tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a mock response based on query and similar tickets."""
        
        # Determine category from similar tickets
        category = "general"
        if similar_tickets:
            top_ticket = similar_tickets[0]
            metadata = top_ticket.get("metadata", {})
            category = metadata.get("category", "general")
        
        # Get response template for category
        template = self.response_templates.get(category, {
            "action": "clarification",
            "responses": ["Could you provide more details about the issue you're experiencing?"]
        })
        
        # Calculate confidence based on similarity scores
        confidence = 0.5
        if similar_tickets:
            top_score = similar_tickets[0].get("score", 0)
            confidence = min(0.9, max(0.3, top_score))
        
        # Determine action based on confidence and similarity
        action = template["action"]
        if confidence < 0.4:
            action = "clarification"
        elif confidence > 0.8 and similar_tickets:
            action = "solution"
        elif not similar_tickets:
            action = "escalation"
        
        # Select appropriate response
        if action == "solution" and category in self.response_templates:
            response = random.choice(self.response_templates[category]["responses"])
        elif action == "clarification":
            response = "Could you provide more details about the issue you're experiencing? This will help me give you a more accurate solution."
        else:
            response = "This seems like a complex issue that would benefit from human assistance. I'll escalate this to our support team."
        
        # Add context from similar tickets if available
        if similar_tickets and action == "solution":
            top_ticket = similar_tickets[0]
            metadata = top_ticket.get("metadata", {})
            if metadata.get("resolution"):
                response += f" Based on a similar case: {metadata['resolution']}"
        
        return {
            "action": action,
            "response": response,
            "confidence": confidence,
            "similar_tickets": similar_tickets
        }