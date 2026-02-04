from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from src.api.routes import router

app = FastAPI(title="AI Support Assistant", version="1.0.0")

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Simple web interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Support Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .query-box { margin: 20px 0; }
            input[type="text"] { width: 70%; padding: 10px; font-size: 16px; }
            button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
            .response { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .examples { margin: 20px 0; }
            .example { display: inline-block; margin: 5px; padding: 5px 10px; background: #e9ecef; cursor: pointer; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 AI Support Assistant</h1>
            <p>Get instant help with your support queries</p>
        </div>
        
        <div class="query-box">
            <input type="text" id="query" placeholder="Describe your issue..." />
            <button onclick="askAssistant()">Ask Assistant</button>
        </div>
        
        <div class="examples">
            <strong>Try these examples:</strong><br>
            <span class="example" onclick="setQuery('I cannot login to my account')">Login Issues</span>
            <span class="example" onclick="setQuery('My payment was declined')">Payment Problems</span>
            <span class="example" onclick="setQuery('The app keeps crashing')">App Crashes</span>
            <span class="example" onclick="setQuery('Website is loading slowly')">Performance Issues</span>
        </div>
        
        <div id="response" class="response" style="display:none;"></div>
        
        <div style="margin-top: 40px; text-align: center;">
            <p><a href="/docs">📚 View API Documentation</a></p>
        </div>
        
        <script>
            function setQuery(text) {
                document.getElementById('query').value = text;
            }
            
            async function askAssistant() {
                const query = document.getElementById('query').value;
                if (!query) return;
                
                const responseDiv = document.getElementById('response');
                responseDiv.innerHTML = '🔍 Searching for similar issues...';
                responseDiv.style.display = 'block';
                
                try {
                    const response = await fetch('/api/v1/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query, max_results: 3 })
                    });
                    
                    const data = await response.json();
                    
                    let html = `
                        <h3>Response: ${data.action.toUpperCase()}</h3>
                        <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(0)}%</p>
                        <p><strong>Suggestion:</strong> ${data.response}</p>
                    `;
                    
                    if (data.similar_tickets && data.similar_tickets.length > 0) {
                        html += '<h4>Similar Past Issues:</h4>';
                        data.similar_tickets.forEach(ticket => {
                            const meta = ticket.metadata || {};
                            html += `<div style="margin: 10px 0; padding: 10px; background: white; border-left: 3px solid #007bff;">
                                <strong>${meta.title || 'Untitled'}</strong><br>
                                ${meta.description || 'No description'}<br>
                                <small>Similarity: ${(ticket.score * 100).toFixed(0)}%</small>
                            </div>`;
                        });
                    }
                    
                    responseDiv.innerHTML = html;
                } catch (error) {
                    responseDiv.innerHTML = '❌ Error: ' + error.message;
                }
            }
            
            document.getElementById('query').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') askAssistant();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/info")
async def info():
    return {
        "message": "AI Support Assistant",
        "version": "1.0.0",
        "interface": "/",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("simple_server:app", host="0.0.0.0", port=8000, reload=True)