import openai
from typing import List, Dict, Any
from config import config

class ResponseGenerator:
    """Generate intelligent responses using LLM based on retrieved context."""
    
    def __init__(self):
        self.client = None
        if config.OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                print("Using demo mode without OpenAI integration")
        self.model = config.LLM_MODEL
    
    def generate_response(self, query: str, similar_tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a response based on the query and similar tickets."""
        
        # Prepare context from similar tickets
        context = self._prepare_context(similar_tickets)
        
        # For demo purposes, if no OpenAI key is provided, use rule-based responses
        if not config.OPENAI_API_KEY or not self.client:
            return self._generate_demo_response(query, similar_tickets)
        
        # Create the prompt
        prompt = self._create_prompt(query, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            
            # Parse the response to extract action type and content
            return self._parse_response(response_text, similar_tickets)
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "action": "escalate",
                "response": "I apologize, but I'm unable to process your request at the moment. Please contact a human agent for assistance.",
                "confidence": 0.0,
                "similar_tickets": []
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM."""
        return """You are an AI support assistant. Your job is to analyze customer queries and provide helpful responses based on similar past tickets.

You should respond in one of three ways:
1. SOLUTION: Provide a direct solution if you find relevant past cases
2. CLARIFICATION: Ask for more details if the query is unclear or needs more information
3. ESCALATION: Recommend human agent involvement for complex or sensitive issues

Format your response as:
ACTION: [SOLUTION|CLARIFICATION|ESCALATION]
CONFIDENCE: [0.0-1.0]
RESPONSE: [Your response text]

Be helpful, concise, and professional."""
    
    def _prepare_context(self, similar_tickets: List[Dict[str, Any]]) -> str:
        """Prepare context string from similar tickets."""
        if not similar_tickets:
            return "No similar tickets found."
        
        context_parts = []
        for i, ticket in enumerate(similar_tickets[:3], 1):  # Use top 3 tickets
            metadata = ticket.get("metadata", {})
            score = ticket.get("score", 0)
            
            context_part = f"""
Ticket {i} (Similarity: {score:.2f}):
Title: {metadata.get('title', 'N/A')}
Issue: {metadata.get('description', 'N/A')}
Category: {metadata.get('category', 'N/A')}
Resolution: {metadata.get('resolution', 'N/A')}
Status: {metadata.get('status', 'N/A')}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create the prompt for the LLM."""
        return f"""
Customer Query: {query}

Similar Past Tickets:
{context}

Based on the customer query and similar past tickets, provide an appropriate response. Consider the similarity scores and relevance of the past tickets when formulating your response.
"""
    
    def _parse_response(self, response_text: str, similar_tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse the LLM response to extract structured information."""
        lines = response_text.strip().split('\n')
        
        action = "escalate"  # default
        confidence = 0.5  # default
        response = response_text  # fallback to full response
        
        for line in lines:
            line = line.strip()
            if line.startswith("ACTION:"):
                action_text = line.replace("ACTION:", "").strip().lower()
                if action_text in ["solution", "clarification", "escalation"]:
                    action = action_text
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.replace("CONFIDENCE:", "").strip())
                except ValueError:
                    confidence = 0.5
            elif line.startswith("RESPONSE:"):
                response = line.replace("RESPONSE:", "").strip()
        
        return {
            "action": action,
            "response": response,
            "confidence": confidence,
            "similar_tickets": similar_tickets
        }
    def _generate_demo_response(self, query: str, similar_tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a demo response without using OpenAI API."""
        query_lower = query.lower()
        
        if not similar_tickets:
            return {
                "action": "clarification",
                "response": "I couldn't find any similar tickets in our database. Could you provide more details about your issue?",
                "confidence": 0.3,
                "similar_tickets": []
            }
        
        # Get the most similar ticket
        top_ticket = similar_tickets[0]
        metadata = top_ticket.get("metadata", {})
        score = top_ticket.get("score", 0)
        
        # Rule-based response generation
        if score > 0.8:
            # High similarity - provide solution
            resolution = metadata.get("resolution", "")
            if resolution:
                return {
                    "action": "solution",
                    "response": f"Based on a similar issue, here's the solution: {resolution}",
                    "confidence": score,
                    "similar_tickets": similar_tickets
                }
        
        if score > 0.6:
            # Medium similarity - provide guidance
            category = metadata.get("category", "")
            title = metadata.get("title", "")
            return {
                "action": "solution",
                "response": f"I found a similar {category} issue: '{title}'. The resolution was: {metadata.get('resolution', 'Please check with support team.')}",
                "confidence": score,
                "similar_tickets": similar_tickets
            }
        
        # Low similarity - ask for clarification
        return {
            "action": "clarification",
            "response": "I found some potentially related tickets, but I need more information to provide the best help. Could you describe your issue in more detail?",
            "confidence": score,
            "similar_tickets": similar_tickets
        }