#!/usr/bin/env python3
"""
AI Support Assistant - Demo Version
Works without sentence-transformers dependency issues
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
import json
import time
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Support Assistant - Demo",
    description="Intelligent customer support with Endee vector database (Demo Mode)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    conversation_id: Optional[str] = "default"

class QueryResponse(BaseModel):
    action: str
    response: str
    confidence: float
    similar_tickets: List[Dict[str, Any]]
    processing_time: float

# Simple embedding service using TF-IDF
class SimpleEmbeddingService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        self.is_fitted = False
        
    def fit_and_transform(self, texts):
        if not self.is_fitted:
            self.vectorizer.fit(texts)
            self.is_fitted = True
        return self.vectorizer.transform(texts).toarray()
    
    def transform(self, texts):
        if not self.is_fitted:
            return np.zeros((len(texts), 100))
        return self.vectorizer.transform(texts).toarray()

# Local vector store
class LocalVectorStore:
    def __init__(self):
        self.vectors = []
        self.metadata = []
        self.ids = []
        
    def add_vector(self, vector_id, embedding, metadata):
        self.vectors.append(embedding)
        self.metadata.append(metadata)
        self.ids.append(vector_id)
        
    def search_similar(self, query_embedding, top_k=5):
        if not self.vectors:
            return []
            
        vectors_array = np.array(self.vectors)
        similarities = cosine_similarity([query_embedding], vectors_array)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                results.append({
                    "id": self.ids[idx],
                    "score": float(similarities[idx]),
                    "metadata": self.metadata[idx]
                })
        
        return results

# Conversational AI
class ConversationalAI:
    def __init__(self):
        self.responses = {
            "authentication": {
                "solutions": [
                    "Try resetting your password using the 'Forgot Password' link.",
                    "Clear your browser cache and cookies, then try logging in again.",
                    "Make sure Caps Lock is off and check for any extra spaces."
                ]
            },
            "billing": {
                "solutions": [
                    "Please check if your payment method is still valid and has sufficient funds.",
                    "Try using a different payment method or contact your bank.",
                    "Verify that your billing address matches your payment method."
                ]
            },
            "technical": {
                "solutions": [
                    "Try refreshing the page or clearing your browser cache.",
                    "Update your app to the latest version.",
                    "Check your internet connection and try again."
                ]
            }
        }
    
    def detect_category(self, query):
        query_lower = query.lower()
        if any(word in query_lower for word in ["login", "password", "account", "sign in"]):
            return "authentication"
        elif any(word in query_lower for word in ["payment", "billing", "card", "charge"]):
            return "billing"
        elif any(word in query_lower for word in ["crash", "error", "bug", "slow"]):
            return "technical"
        return "general"
    
    def generate_response(self, query, similar_tickets):
        category = self.detect_category(query)
        confidence = 0.7 if similar_tickets else 0.5
        
        if similar_tickets and similar_tickets[0]["score"] > 0.6:
            # High confidence solution
            top_ticket = similar_tickets[0]
            resolution = top_ticket["metadata"].get("resolution", "")
            
            if category in self.responses:
                base_response = np.random.choice(self.responses[category]["solutions"])
            else:
                base_response = "Based on similar cases, here's what typically helps:"
            
            response = f"{base_response}"
            if resolution:
                response += f" In a similar case: {resolution}"
            
            return {
                "action": "solution",
                "response": response,
                "confidence": confidence,
                "similar_tickets": similar_tickets
            }
        elif confidence > 0.4:
            return {
                "action": "clarification", 
                "response": f"I'd like to help you with your {category} issue. Can you provide more details about what exactly happened?",
                "confidence": confidence,
                "similar_tickets": similar_tickets
            }
        else:
            return {
                "action": "escalation",
                "response": "This seems like a complex issue. I'll connect you with a human support agent who can provide personalized assistance.",
                "confidence": confidence,
                "similar_tickets": similar_tickets
            }

# Global instances
embedding_service = SimpleEmbeddingService()
vector_store = LocalVectorStore()
ai_assistant = ConversationalAI()

# Sample data
SAMPLE_TICKETS = [
    {
        "id": "ticket_001",
        "title": "Cannot login to account",
        "description": "User is unable to login with correct credentials. Getting 'invalid password' error.",
        "category": "authentication",
        "resolution": "Password reset required. User had caps lock enabled."
    },
    {
        "id": "ticket_002",
        "title": "Payment failed",
        "description": "Credit card payment is being declined during checkout.",
        "category": "billing", 
        "resolution": "Issue with payment processor. User switched to different card."
    },
    {
        "id": "ticket_003",
        "title": "App crashes on startup",
        "description": "Mobile app crashes immediately after opening.",
        "category": "technical",
        "resolution": "App update required. User updated to latest version."
    },
    {
        "id": "ticket_004",
        "title": "Forgot password",
        "description": "User forgot their password and needs to reset it.",
        "category": "authentication",
        "resolution": "Sent password reset link to registered email address."
    },
    {
        "id": "ticket_005",
        "title": "Website loading slowly",
        "description": "Website pages are loading very slowly, taking over 30 seconds.",
        "category": "technical",
        "resolution": "Server optimization performed. CDN cache cleared."
    }
]

def initialize_system():
    """Initialize the system with sample data."""
    logger.info("🚀 Initializing AI Support Assistant (Demo Mode)")
    
    # Prepare texts for embedding
    texts = []
    for ticket in SAMPLE_TICKETS:
        text = f"{ticket['title']} {ticket['description']} {ticket['category']}"
        texts.append(text)
    
    # Generate embeddings
    embeddings = embedding_service.fit_and_transform(texts)
    
    # Add to vector store
    for i, ticket in enumerate(SAMPLE_TICKETS):
        vector_store.add_vector(
            ticket["id"],
            embeddings[i],
            {
                "title": ticket["title"],
                "description": ticket["description"],
                "category": ticket["category"],
                "resolution": ticket["resolution"]
            }
        )
    
    logger.info(f"✅ Loaded {len(SAMPLE_TICKETS)} sample tickets")

# Initialize on startup
initialize_system()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the chat interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Support Assistant - Demo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .chat-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 800px;
                height: 600px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .chat-header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .chat-header h1 { font-size: 1.8em; margin-bottom: 5px; }
            .chat-header p { opacity: 0.9; font-size: 0.9em; }
            .status-badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.7em;
                margin-top: 5px;
                background: rgba(255,255,255,0.2);
            }
            
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            .message {
                margin-bottom: 20px;
                display: flex;
                align-items: flex-start;
                gap: 10px;
            }
            .message.user { flex-direction: row-reverse; }
            .message-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2em;
                flex-shrink: 0;
            }
            .message.user .message-avatar { background: #007bff; color: white; }
            .message.assistant .message-avatar { background: #28a745; color: white; }
            .message-content {
                background: white;
                padding: 15px;
                border-radius: 15px;
                max-width: 70%;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .message.user .message-content { background: #007bff; color: white; }
            
            .action-badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.7em;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 8px;
            }
            .action-solution { background: #d4edda; color: #155724; }
            .action-clarification { background: #fff3cd; color: #856404; }
            .action-escalation { background: #f8d7da; color: #721c24; }
            
            .chat-input {
                padding: 20px;
                background: white;
                border-top: 1px solid #e9ecef;
            }
            .input-group {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            .chat-input input {
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            .chat-input input:focus { border-color: #007bff; }
            .send-btn {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: transform 0.2s;
            }
            .send-btn:hover { transform: translateY(-2px); }
            .send-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
            
            .quick-actions {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 15px;
            }
            .quick-action {
                background: #e9ecef;
                border: none;
                padding: 8px 12px;
                border-radius: 15px;
                font-size: 0.8em;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .quick-action:hover { background: #dee2e6; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>🤖 AI Support Assistant</h1>
                <p>Semantic Search Demo with Vector Database</p>
                <div class="status-badge">✅ Demo Mode Active</div>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <p>Hello! I'm your AI support assistant running in demo mode.</p>
                        <p style="margin-top: 10px;">I use semantic vector search to find similar support tickets and provide intelligent responses. Try asking about login issues, payment problems, or technical difficulties!</p>
                        <p style="margin-top: 10px;">What can I help you with today?</p>
                    </div>
                </div>
            </div>
            
            <div class="chat-input">
                <div class="quick-actions">
                    <button class="quick-action" onclick="sendQuickMessage('I cannot login to my account')">Login Issues</button>
                    <button class="quick-action" onclick="sendQuickMessage('My payment was declined')">Payment Problems</button>
                    <button class="quick-action" onclick="sendQuickMessage('The app keeps crashing')">App Crashes</button>
                    <button class="quick-action" onclick="sendQuickMessage('Website is loading slowly')">Performance Issues</button>
                </div>
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Describe your issue..." />
                    <button class="send-btn" onclick="sendMessage()" id="sendBtn">Send</button>
                </div>
            </div>
        </div>

        <script>
            function addMessage(content, isUser = false, data = null) {
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
                
                if (isUser) {
                    messageDiv.innerHTML = `
                        <div class="message-avatar">👤</div>
                        <div class="message-content">${content}</div>
                    `;
                } else {
                    let messageContent = `<div class="message-content">`;
                    
                    if (data && data.action) {
                        messageContent += `<div class="action-badge action-${data.action}">${data.action}</div>`;
                    }
                    
                    messageContent += `<p>${content}</p>`;
                    
                    if (data && data.confidence) {
                        messageContent += `<p style="font-size: 0.8em; color: #6c757d; margin-top: 8px;">
                            Confidence: ${(data.confidence * 100).toFixed(0)}% | 
                            Response time: ${(data.processing_time * 1000).toFixed(0)}ms
                        </p>`;
                    }
                    
                    if (data && data.similar_tickets && data.similar_tickets.length > 0) {
                        messageContent += `<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e9ecef;">
                            <strong style="font-size: 0.9em;">📚 Similar past issues:</strong>`;
                        
                        data.similar_tickets.slice(0, 2).forEach(ticket => {
                            const meta = ticket.metadata || {};
                            messageContent += `
                                <div style="margin: 8px 0; padding: 8px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #007bff;">
                                    <strong style="font-size: 0.85em;">${meta.title || 'Untitled'}</strong><br>
                                    <small style="color: #6c757d;">Similarity: ${(ticket.score * 100).toFixed(0)}%</small>
                                </div>
                            `;
                        });
                        messageContent += `</div>`;
                    }
                    
                    messageContent += `</div>`;
                    
                    messageDiv.innerHTML = `
                        <div class="message-avatar">🤖</div>
                        ${messageContent}
                    `;
                }
                
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                const sendBtn = document.getElementById('sendBtn');
                sendBtn.disabled = true;
                sendBtn.textContent = 'Processing...';
                
                // Add user message
                addMessage(message, true);
                input.value = '';
                
                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            query: message, 
                            max_results: 3
                        })
                    });
                    
                    const data = await response.json();
                    addMessage(data.response, false, data);
                    
                } catch (error) {
                    addMessage('Sorry, I encountered an error. Please try again.', false);
                    console.error('Error:', error);
                } finally {
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Send';
                }
            }
            
            function sendQuickMessage(message) {
                document.getElementById('messageInput').value = message;
                sendMessage();
            }
            
            // Enter key to send
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """Handle support queries using semantic search."""
    start_time = time.time()
    
    try:
        logger.info(f"🔍 Processing query: '{request.query[:50]}...'")
        
        # Generate embedding for query
        query_embedding = embedding_service.transform([request.query])[0]
        
        # Search similar tickets
        similar_tickets = vector_store.search_similar(query_embedding, request.max_results)
        
        # Generate AI response
        result = ai_assistant.generate_response(request.query, similar_tickets)
        
        processing_time = time.time() - start_time
        result["processing_time"] = processing_time
        
        logger.info(f"✅ Response: {result['action']} ({processing_time:.3f}s)")
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Query error: {e}")
        processing_time = time.time() - start_time
        
        return QueryResponse(
            action="escalation",
            response="I apologize, but I'm experiencing technical difficulties. Please contact support.",
            confidence=0.0,
            similar_tickets=[],
            processing_time=processing_time
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": "demo",
        "endee_connected": False,
        "vector_store": "Local TF-IDF",
        "tickets_loaded": len(SAMPLE_TICKETS)
    }

@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    return {
        "mode": "demo",
        "vector_store": "Local TF-IDF",
        "embedding_model": "TF-IDF Vectorizer",
        "tickets_count": len(SAMPLE_TICKETS),
        "features": 100,
        "similarity_metric": "cosine"
    }

if __name__ == "__main__":
    uvicorn.run("demo_app:app", host="0.0.0.0", port=8000, reload=True)