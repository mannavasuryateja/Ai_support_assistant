
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SupportTicket(BaseModel):
    
    id: Optional[str] = Field(None, description="Unique ticket identifier")
    title: str = Field(..., description="Ticket title/subject")
    description: str = Field(..., description="Detailed description of the issue")
    category: str = Field("general", description="Issue category (e.g., authentication, billing)")
    status: str = Field("open", description="Ticket status (open, resolved, closed)")
    resolution: str = Field("", description="Resolution details if resolved")
    priority: str = Field("medium", description="Priority level (low, medium, high, critical)")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    resolved_at: Optional[str] = Field(None, description="Resolution timestamp")

    class Config:
        schema_extra = {
            "example": {
                "title": "Cannot login to account",
                "description": "User is unable to login with correct credentials",
                "category": "authentication",
                "status": "open",
                "priority": "high"
            }
        }

class QueryRequest(BaseModel):
    
    query: str = Field(..., description="User's support query", min_length=1)
    category: Optional[str] = Field(None, description="Optional category filter")
    max_results: Optional[int] = Field(5, description="Maximum number of similar tickets to return", ge=1, le=20)
    conversation_id: Optional[str] = Field("default", description="Conversation identifier for context")

    class Config:
        schema_extra = {
            "example": {
                "query": "I can't login to my account",
                "category": "authentication",
                "max_results": 5
            }
        }

class SimilarTicket(BaseModel):
    
    id: str = Field(..., description="Ticket identifier")
    score: float = Field(..., description="Similarity score (0-1)")
    metadata: Dict[str, Any] = Field(..., description="Ticket metadata")

class QueryResponse(BaseModel):
    
    action: str = Field(..., description="Response action type (solution, clarification, escalation)")
    response: str = Field(..., description="AI-generated response text")
    confidence: float = Field(..., description="Response confidence score (0-1)")
    similar_tickets: List[SimilarTicket] = Field(default=[], description="List of similar historical tickets")
    processing_time: float = Field(..., description="Query processing time in seconds")
    conversation_id: str = Field("default", description="Conversation identifier")

    class Config:
        schema_extra = {
            "example": {
                "action": "solution",
                "response": "Try resetting your password using the 'Forgot Password' link.",
                "confidence": 0.85,
                "similar_tickets": [
                    {
                        "id": "ticket_001",
                        "score": 0.92,
                        "metadata": {
                            "title": "Cannot login to account",
                            "resolution": "Password reset required"
                        }
                    }
                ],
                "processing_time": 0.045
            }
        }

class TicketInsertRequest(BaseModel):
    """Model for batch ticket insertion requests."""
    tickets: List[SupportTicket] = Field(..., description="List of tickets to insert")

    class Config:
        schema_extra = {
            "example": {
                "tickets": [
                    {
                        "title": "Payment declined",
                        "description": "Credit card payment was declined during checkout",
                        "category": "billing",
                        "status": "resolved",
                        "resolution": "User contacted bank, transaction approved"
                    }
                ]
            }
        }

class TicketInsertResponse(BaseModel):
    
    success: bool = Field(..., description="Overall operation success")
    inserted_count: int = Field(..., description="Number of successfully inserted tickets")
    failed_count: int = Field(..., description="Number of failed insertions")
    total_count: int = Field(..., description="Total number of tickets processed")
    message: str = Field(..., description="Detailed result message")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "inserted_count": 5,
                "failed_count": 0,
                "total_count": 5,
                "message": "Processed 5 tickets: 5 successful, 0 failed"
            }
        }

class HealthResponse(BaseModel):
    
    status: str = Field(..., description="Overall system status (healthy, unhealthy, error)")
    endee_connected: bool = Field(..., description="Endee database connection status")
    vector_store: str = Field(..., description="Vector store type (Endee, Local)")
    embedding_model: str = Field(..., description="Embedding model name")
    collection_name: str = Field(..., description="Vector collection name")
    ticket_count: int = Field(..., description="Number of tickets in database")
    using_endee: bool = Field(..., description="Whether Endee is being used")
    error: Optional[str] = Field(None, description="Error message if status is error")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "endee_connected": True,
                "vector_store": "Endee",
                "embedding_model": "all-MiniLM-L6-v2",
                "collection_name": "support_tickets",
                "ticket_count": 150,
                "using_endee": True
            }
        }

class SystemStats(BaseModel):
    
    initialized: bool = Field(..., description="System initialization status")
    using_endee: bool = Field(..., description="Whether Endee is being used")
    vector_store: str = Field(..., description="Vector store type")
    embedding_model: str = Field(..., description="Embedding model name")
    embedding_dimension: int = Field(..., description="Embedding vector dimension")
    similarity_threshold: float = Field(..., description="Similarity threshold for matches")
    max_results: int = Field(..., description="Maximum results per query")
    collection_name: str = Field(..., description="Vector collection name")
    endee_url: Optional[str] = Field(None, description="Endee server URL")
    ticket_count: int = Field(..., description="Number of tickets in database")

    class Config:
        schema_extra = {
            "example": {
                "initialized": True,
                "using_endee": True,
                "vector_store": "Endee",
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": 384,
                "similarity_threshold": 0.7,
                "max_results": 5,
                "collection_name": "support_tickets",
                "endee_url": "http://localhost:8080",
                "ticket_count": 150
            }
        }

class ErrorResponse(BaseModel):
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")

    class Config:
        schema_extra = {
            "example": {
                "error": "Query processing failed",
                "detail": "Failed to generate embedding for query",
                "timestamp": "2024-02-03T10:30:45Z"
            }
        }
