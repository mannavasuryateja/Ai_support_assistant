#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
logging.getLogger("src.vector_store.endee_client").setLevel(logging.DEBUG)
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.routes import router
from src.support_assistant import SupportAssistant
from config import config


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI Support Assistant with Endee",
    description="Intelligent customer support using Endee vector database for semantic search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api/v1", tags=["Support Assistant"])

# Global assistant instance
assistant = None

@app.on_event("startup")
async def startup_event():
    
    global assistant
    logger.info("🚀 Starting AI Support Assistant...")
    
    try:
        assistant = SupportAssistant()
        success = assistant.initialize()
        
        if success:
            logger.info("✅ Support Assistant initialized successfully")
            
            # Log system status
            stats = assistant.get_stats()
            logger.info(f"📊 System Status:")
            logger.info(f"   Vector Store: {stats.get('vector_store', 'Unknown')}")
            logger.info(f"   Using Endee: {stats.get('using_endee', False)}")
            logger.info(f"   Collection: {stats.get('collection_name', 'N/A')}")
            
        else:
            logger.error("❌ Failed to initialize Support Assistant")
            
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down AI Support Assistant...")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main chat interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Support Assistant</title>
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
            
            .typing-indicator {
                display: none;
                align-items: center;
                gap: 10px;
                margin-bottom: 20px;
            }
            .typing-dots {
                display: flex;
                gap: 4px;
            }
            .typing-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #007bff;
                animation: typing 1.4s infinite;
            }
            .typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .typing-dot:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-10px); }
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>🤖 AI Support Assistant</h1>
                <p>Powered by Endee Vector Database</p>
                <div class="status-badge" id="statusBadge">Connecting...</div>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <p>Hello! I'm your AI support assistant powered by Endee vector database.</p>
                        <p style="margin-top: 10px;">I can help you with login issues, payment problems, technical difficulties, and more using semantic search to find the most relevant solutions.</p>
                        <p style="margin-top: 10px;">What can I help you with today?</p>
                    </div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                <div class="message-avatar" style="background: #28a745; color: white;">🤖</div>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span style="font-size: 0.9em; color: #6c757d;">Searching knowledge base...</span>
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
            let conversationId = 'conv_' + Date.now();
            
            // Check system status on load
            window.onload = function() {
                checkSystemStatus();
            };
            
            async function checkSystemStatus() {
                try {
                    const response = await fetch('/api/v1/health');
                    const data = await response.json();
                    const statusBadge = document.getElementById('statusBadge');
                    
                    if (data.endee_connected) {
                        statusBadge.textContent = '✅ Endee Connected';
                        statusBadge.style.background = 'rgba(40, 167, 69, 0.8)';
                    } else {
                        statusBadge.textContent = '⚠️ Demo Mode';
                        statusBadge.style.background = 'rgba(255, 193, 7, 0.8)';
                    }
                } catch (error) {
                    const statusBadge = document.getElementById('statusBadge');
                    statusBadge.textContent = '❌ Offline';
                    statusBadge.style.background = 'rgba(220, 53, 69, 0.8)';
                }
            }
            
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
                            Response time: ${data.processing_time ? (data.processing_time * 1000).toFixed(0) + 'ms' : 'N/A'}
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
            
            function showTyping() {
                document.getElementById('typingIndicator').style.display = 'flex';
                document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
            }
            
            function hideTyping() {
                document.getElementById('typingIndicator').style.display = 'none';
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                const sendBtn = document.getElementById('sendBtn');
                sendBtn.disabled = true;
                
                // Add user message
                addMessage(message, true);
                input.value = '';
                
                // Show typing indicator
                showTyping();
                
                try {
                    const response = await fetch('/api/v1/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            query: message, 
                            max_results: 3,
                            conversation_id: conversationId
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Hide typing and add response
                    hideTyping();
                    addMessage(data.response, false, data);
                    
                } catch (error) {
                    hideTyping();
                    addMessage('Sorry, I encountered an error. Please try again or contact support.', false);
                    console.error('Error:', error);
                } finally {
                    sendBtn.disabled = false;
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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global assistant
    
    if assistant is None:
        return {
            "status": "initializing",
            "endee_connected": False,
            "message": "Assistant is starting up"
        }
    
    stats = assistant.get_stats()
    
    return {
        "status": "healthy" if stats.get("initialized", False) else "unhealthy",
        "endee_connected": stats.get("using_endee", False),
        "vector_store": stats.get("vector_store", "Unknown"),
        "collection": stats.get("collection_name", "N/A"),
        "embedding_model": stats.get("embedding_model", "N/A")
    }

@app.get("/info")
async def app_info():
    """Application information."""
    return {
        "name": "AI Support Assistant",
        "version": "1.0.0",
        "description": "Intelligent customer support using Endee vector database",
        "endpoints": {
            "chat": "/",
            "api_docs": "/docs",
            "health": "/health",
            "query": "/api/v1/query"
        }
    }

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
        log_level="info"
    )
