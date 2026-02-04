from typing import List, Dict, Any
import random
import re

class ConversationalLLM:
    """Enhanced conversational LLM for interactive support assistance."""
    
    def __init__(self):
        self.conversation_patterns = {
            "autopay": {
                "keywords": ["autopay", "auto pay", "automatic payment", "recurring payment"],
                "follow_up_questions": [
                    "When did you set up the autopay?",
                    "What error message are you seeing?",
                    "Which payment method is linked to your autopay?",
                    "Is this the first time autopay has failed?"
                ],
                "solutions": [
                    "Check if your payment method has sufficient funds or hasn't expired.",
                    "Verify that your bank hasn't blocked the transaction.",
                    "Try updating your payment method in account settings."
                ]
            },
            "login": {
                "keywords": ["login", "sign in", "password", "account access", "authentication"],
                "follow_up_questions": [
                    "Are you getting a specific error message?",
                    "When was the last time you successfully logged in?",
                    "Are you using the correct email address?",
                    "Have you tried resetting your password?"
                ],
                "solutions": [
                    "Try resetting your password using the 'Forgot Password' link.",
                    "Clear your browser cache and cookies.",
                    "Make sure Caps Lock is off and check for typos."
                ]
            },
            "billing": {
                "keywords": ["billing", "subscription", "cancel", "refund", "charge", "google", "delete subscription"],
                "follow_up_questions": [
                    "What service are you trying to cancel?",
                    "When was the last charge made?",
                    "Do you have the subscription ID or order number?",
                    "Are you looking for a refund or just to cancel future charges?"
                ],
                "solutions": [
                    "Go to your account settings and look for 'Subscriptions' or 'Billing'.",
                    "Contact the service provider directly for subscription cancellations.",
                    "Check your email for subscription management links."
                ]
            },
            "payment": {
                "keywords": ["payment", "credit card", "declined", "transaction"],
                "follow_up_questions": [
                    "What type of payment method are you using?",
                    "What error message did you receive?",
                    "Is this a new payment method or one you've used before?",
                    "Have you contacted your bank about this transaction?"
                ],
                "solutions": [
                    "Contact your bank to ensure the transaction isn't being blocked.",
                    "Try using a different payment method.",
                    "Verify that your billing address matches your payment method."
                ]
            },
            "app_crash": {
                "keywords": ["crash", "app crash", "freezing", "not responding", "closes"],
                "follow_up_questions": [
                    "What device are you using (iOS/Android/Desktop)?",
                    "When does the app crash - on startup or during use?",
                    "Have you updated the app recently?",
                    "Are you getting any error messages?"
                ],
                "solutions": [
                    "Update the app to the latest version.",
                    "Restart your device and try again.",
                    "Clear the app cache or reinstall the app."
                ]
            },
            "performance": {
                "keywords": ["slow", "loading", "performance", "lag", "timeout"],
                "follow_up_questions": [
                    "Which specific pages or features are slow?",
                    "What internet connection are you using?",
                    "Are you experiencing this on all devices?",
                    "When did you first notice the slowness?"
                ],
                "solutions": [
                    "Clear your browser cache and cookies.",
                    "Try using a different browser or device.",
                    "Check your internet connection speed."
                ]
            }
        }
        
        self.conversation_state = {}  # Store conversation context
    
    def detect_category(self, query: str) -> str:
        """Detect the category of the user query."""
        query_lower = query.lower()
        
        for category, data in self.conversation_patterns.items():
            for keyword in data["keywords"]:
                if keyword in query_lower:
                    return category
        
        return "general"
    
    def needs_clarification(self, query: str, similar_tickets: List[Dict[str, Any]], conversation_id: str = "default") -> bool:
        """Determine if we need to ask follow-up questions."""
        
        # Check if we've already asked questions in this conversation
        if conversation_id in self.conversation_state:
            asked_count = len(self.conversation_state[conversation_id].get("asked_questions", []))
            # Stop asking after 2 questions to avoid repetition
            if asked_count >= 2:
                return False
        
        # If query has specific details, don't ask for clarification
        specific_indicators = [
            "yesterday", "today", "last week", "error message", "declined", "failed",
            "cannot", "can't", "won't", "doesn't work", "not working", "crashed",
            "slow", "timeout", "expired", "blocked", "suspended", "google", "dollars"
        ]
        
        query_lower = query.lower()
        if any(indicator in query_lower for indicator in specific_indicators):
            return False
        
        # If we have good similar tickets, provide solution instead
        if similar_tickets and similar_tickets[0].get("score", 0) > 0.6:
            return False
        
        # If query is very short or vague, ask for clarification
        if len(query.split()) < 4:
            return True
        
        # Check for very vague terms only
        very_vague_terms = ["issue", "problem", "help me"]
        if any(term in query_lower for term in very_vague_terms) and len(query.split()) < 5:
            return True
        
        return False
    
    def generate_follow_up_question(self, query: str, conversation_id: str = "default") -> str:
        """Generate a relevant follow-up question."""
        category = self.detect_category(query)
        
        if category in self.conversation_patterns:
            questions = self.conversation_patterns[category]["follow_up_questions"]
            
            # Track which questions we've already asked
            if conversation_id not in self.conversation_state:
                self.conversation_state[conversation_id] = {"asked_questions": [], "category": category}
            
            # Find a question we haven't asked yet
            available_questions = [q for q in questions if q not in self.conversation_state[conversation_id]["asked_questions"]]
            
            if available_questions:
                question = random.choice(available_questions)
                self.conversation_state[conversation_id]["asked_questions"].append(question)
                return question
        
        # Generic follow-up questions
        generic_questions = [
            "Can you provide more details about what exactly happened?",
            "What error message are you seeing, if any?",
            "When did this issue first start?",
            "Have you tried any troubleshooting steps already?"
        ]
        
        return random.choice(generic_questions)
    
    def generate_response(self, query: str, similar_tickets: List[Dict[str, Any]], conversation_id: str = "default") -> Dict[str, Any]:
        """Generate a conversational response."""
        
        category = self.detect_category(query)
        
        # Initialize conversation state if needed
        if conversation_id not in self.conversation_state:
            self.conversation_state[conversation_id] = {
                "asked_questions": [], 
                "category": category,
                "context": []
            }
        
        # Add current query to context
        self.conversation_state[conversation_id]["context"].append(query)
        
        # Special handling for specific scenarios
        query_lower = query.lower()
        
        # Handle Google subscription cancellation specifically
        if "google" in query_lower and ("delete" in query_lower or "cancel" in query_lower):
            response_text = "I understand you want to cancel a Google service subscription. Here's how to do it:\n\n"
            response_text += "1. Go to subscriptions.google.com\n"
            response_text += "2. Find the subscription you want to cancel\n"
            response_text += "3. Click 'Cancel subscription'\n"
            response_text += "4. Follow the prompts to confirm\n\n"
            response_text += "For refunds, you'll need to contact Google Support directly. Would you like me to help you with anything else regarding this cancellation?"
            
            return {
                "action": "solution",
                "response": response_text,
                "confidence": 0.9,
                "similar_tickets": similar_tickets,
                "category": "billing"
            }
        
        # Check if we need clarification
        if self.needs_clarification(query, similar_tickets, conversation_id):
            follow_up = self.generate_follow_up_question(query, conversation_id)
            
            response_text = f"I'd like to help you with your {category} issue. {follow_up}"
            
            # Add context from similar tickets if available
            if similar_tickets:
                top_ticket = similar_tickets[0]
                metadata = top_ticket.get("metadata", {})
                if metadata.get("resolution"):
                    response_text += f"\n\nWhile you provide more details, here's what worked for a similar issue: {metadata['resolution']}"
            
            return {
                "action": "clarification",
                "response": response_text,
                "confidence": 0.6,
                "similar_tickets": similar_tickets,
                "follow_up_question": follow_up,
                "category": category
            }
        
        # Generate solution-based response with context awareness
        confidence = 0.5
        if similar_tickets:
            top_score = similar_tickets[0].get("score", 0)
            confidence = min(0.95, max(0.4, top_score))
        
        # Check if user provided more details in follow-up
        context = self.conversation_state[conversation_id].get("context", [])
        if len(context) > 1:
            # User has provided follow-up information
            response_text = "Thank you for the additional details. "
            confidence = max(confidence, 0.8)  # Increase confidence with more context
        else:
            response_text = ""
        
        if confidence > 0.7 or len(context) > 1:
            # High confidence solution or follow-up response
            if category in self.conversation_patterns:
                solution = random.choice(self.conversation_patterns[category]["solutions"])
            else:
                solution = "Based on similar cases, here's what typically resolves this issue:"
            
            response_text += f"{solution}"
            
            if similar_tickets:
                top_ticket = similar_tickets[0]
                metadata = top_ticket.get("metadata", {})
                if metadata.get("resolution"):
                    response_text += f"\n\nSpecifically, in a similar case: {metadata['resolution']}"
            
            response_text += f"\n\nIf this doesn't resolve your issue, please let me know and I'll connect you with a human agent who can provide more personalized assistance."
            
            return {
                "action": "solution",
                "response": response_text,
                "confidence": confidence,
                "similar_tickets": similar_tickets,
                "category": category
            }
        
        elif confidence > 0.4:
            # Medium confidence - provide solution but ask for feedback
            response_text += f"Based on similar {category} issues, here are some steps that often help:\n\n"
            
            if category in self.conversation_patterns:
                solutions = self.conversation_patterns[category]["solutions"]
                for i, solution in enumerate(solutions[:2], 1):
                    response_text += f"{i}. {solution}\n"
            
            response_text += f"\nPlease try these steps and let me know if the issue persists. If needed, I can escalate this to our support team for further assistance."
            
            return {
                "action": "solution",
                "response": response_text,
                "confidence": confidence,
                "similar_tickets": similar_tickets,
                "category": category
            }
        
        else:
            # Low confidence - escalate but offer to help more
            response_text += f"I understand you're having a {category} issue. While I don't have an exact match for your specific situation, I'd like to help you further.\n\n"
            response_text += f"Would you like me to:\n1. Ask you a few more questions to better understand the issue\n2. Connect you directly with a human support agent\n\nOur support team specializes in {category} issues and can provide personalized assistance."
            
            return {
                "action": "escalation",
                "response": response_text,
                "confidence": confidence,
                "similar_tickets": similar_tickets,
                "category": category
            }