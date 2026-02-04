from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.api.routes import router
from config import config

# Create FastAPI application
app = FastAPI(
    title="AI-Powered Support Assistant",
    description="An intelligent customer support system using semantic vector search",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(router, prefix="/api/v1")

# Add the home route to main app
@app.get("/")
async def home():
    """Serve the web interface."""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

from fastapi.responses import HTMLResponse

@app.get("/info")
async def info():
    """Root endpoint with basic information."""
    return {
        "message": "AI-Powered Support Assistant",
        "version": "1.0.0",
        "interface": "/",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )