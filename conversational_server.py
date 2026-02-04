from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from src.api.routes import router

app = FastAPI(title="AI Support Assistant - Conversational", version="1.0.0")

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Enhanced conversational web interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Support Assistant</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            .message.user {
                flex-direction: row-reverse;
            }
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
            .message.user .message-avatar {
                background: #007bff;
                color: white;
            }
            .message.assistant .message-avatar {
                background: #28a745;
                color: white;
            }
            .message-content {
                background: white;
                padding: 15px;
                border-radius: 15px;
                max-width: 70%;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .message.user .message-content {
                background: #007bff;
                color: white;
            }
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
            
            .similar-tickets {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e9ecef;
            }
            .similar-ticket {
                background: #f8f9fa;
                padding: 10px;
                border-radius: 8px;
                margin: 8px 0;
                border-left: 3px solid #007bff;
                font-size: 0.9em;
            }
            
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
            .chat-input input:focus {
                border-color: #007bff;
            }
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
                <p>I'm here to help with your support questions</p>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <p>Hello! I'm your AI support assistant. I can help you with login issues, payment problems, technical difficulties, and more.</p>
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
                <span style="font-size: 0.9em; color: #6c757d;">Assistant is typing...</span>
            </div>
            
            <div class="chat-input">
                <div class="quick-actions">
                    <button class="quick-action" onclick="sendQuickMessage('I have an autopay issue')">Autopay Issue</button>
                    <button class="quick-action" onclick="sendQuickMessage('Cannot login to my account')">Login Problem</button>
                    <button class="quick-action" onclick="sendQuickMessage('My payment was declined')">Payment Issue</button>
                    <button class="quick-action" onclick="sendQuickMessage('App keeps crashing')">App Crash</button>
                </div>
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Type your message..." />
                    <button class="send-btn" onclick="sendMessage()" id="sendBtn">Send</button>
                </div>
            </div>
        </div>

        <script>
            let conversationId = 'conv_' + Date.now();
            
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
                        messageContent += `<p style="font-size: 0.8em; color: #6c757d; margin-top: 8px;">Confidence: ${(data.confidence * 100).toFixed(0)}%</p>`;
                    }
                    
                    if (data && data.similar_tickets && data.similar_tickets.length > 0) {
                        messageContent += `<div class="similar-tickets">
                            <strong style="font-size: 0.9em;">Similar past issues:</strong>`;
                        
                        data.similar_tickets.slice(0, 2).forEach(ticket => {
                            const meta = ticket.metadata || {};
                            messageContent += `
                                <div class="similar-ticket">
                                    <strong>${meta.title || 'Untitled'}</strong><br>
                                    <small>Similarity: ${(ticket.score * 100).toFixed(0)}%</small>
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
                    addMessage('Sorry, I encountered an error. Please try again.', false);
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

if __name__ == "__main__":
    uvicorn.run("conversational_server:app", host="0.0.0.0", port=8000, reload=True)