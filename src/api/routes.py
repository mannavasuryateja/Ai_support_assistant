

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import time
import logging

from .models import (
    QueryRequest, QueryResponse, 
    TicketInsertRequest, TicketInsertResponse, 
    SupportTicket, SystemStats, HealthResponse
)
from ..support_assistant import SupportAssistant

logger = logging.getLogger(__name__)


router = APIRouter()


_assistant_instance = None

def get_assistant() -> SupportAssistant:
    
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = SupportAssistant()
        _assistant_instance.initialize()
    return _assistant_instance

@router.post("/query", response_model=QueryResponse)
async def handle_support_query(
    request: QueryRequest, 
    assistant: SupportAssistant = Depends(get_assistant)
):
    
    start_time = time.time()
    
    try:
        logger.info(f"🔍 API Query: '{request.query[:50]}...'")
        
        result = assistant.handle_query(
            query=request.query,
            category=request.category,
            max_results=request.max_results,
            conversation_id=getattr(request, 'conversation_id', 'api_default')
        )
        
        processing_time = time.time() - start_time
        
        response = QueryResponse(
            action=result["action"],
            response=result["response"],
            confidence=result["confidence"],
            similar_tickets=result["similar_tickets"],
            processing_time=processing_time,
            conversation_id=getattr(request, 'conversation_id', 'api_default')
        )
        
        logger.info(f"✅ API Response: {result['action']} ({processing_time:.3f}s)")
        return response
        
    except Exception as e:
        logger.error(f"❌ API Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/tickets", response_model=TicketInsertResponse)
async def insert_tickets(
    request: TicketInsertRequest,
    assistant: SupportAssistant = Depends(get_assistant)
):
    
    try:
        logger.info(f"📦 API Batch Insert: {len(request.tickets)} tickets")
        
        
        ticket_dicts = [ticket.dict() for ticket in request.tickets]
        
        # Process batch insertion
        results = assistant.add_tickets_batch(ticket_dicts)
        
        response = TicketInsertResponse(
            success=results["failed_count"] == 0,
            inserted_count=results["success_count"],
            failed_count=results["failed_count"],
            total_count=results["total"],
            message=f"Processed {results['total']} tickets: {results['success_count']} successful, {results['failed_count']} failed"
        )
        
        logger.info(f"✅ API Batch Complete: {results['success_count']}/{results['total']} successful")
        return response
        
    except Exception as e:
        logger.error(f"❌ API Batch Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error inserting tickets: {str(e)}"
        )

@router.post("/tickets/single", response_model=dict)
async def insert_single_ticket(
    ticket: SupportTicket,
    assistant: SupportAssistant = Depends(get_assistant)
):
    """Insert a single support ticket."""
    try:
        success = assistant.add_ticket(ticket.dict())
        
        if success:
            return {
                "success": True,
                "message": f"Ticket '{ticket.title}' added successfully",
                "ticket_id": ticket.id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to insert ticket"
            )
            
    except Exception as e:
        logger.error(f"❌ Single ticket insert error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inserting ticket: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
async def health_check(assistant: SupportAssistant = Depends(get_assistant)):
    
    try:
        health_data = assistant.health_check()
        stats = assistant.get_stats()
        
        return HealthResponse(
            status="healthy" if health_data["system_initialized"] else "unhealthy",
            endee_connected=health_data.get("endee_available", False),
            vector_store=stats.get("vector_store", "Unknown"),
            embedding_model=stats.get("embedding_model", "Unknown"),
            collection_name=stats.get("collection_name", "Unknown"),
            ticket_count=stats.get("ticket_count", 0),
            using_endee=stats.get("using_endee", False)
        )
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return HealthResponse(
            status="error",
            endee_connected=False,
            vector_store="Error",
            embedding_model="Error",
            collection_name="Error",
            ticket_count=0,
            using_endee=False,
            error=str(e)
        )

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(assistant: SupportAssistant = Depends(get_assistant)):
    """Get detailed system statistics and configuration."""
    try:
        stats = assistant.get_stats()
        
        return SystemStats(
            initialized=stats["initialized"],
            using_endee=stats["using_endee"],
            vector_store=stats["vector_store"],
            embedding_model=stats["embedding_model"],
            embedding_dimension=stats["embedding_dimension"],
            similarity_threshold=stats["similarity_threshold"],
            max_results=stats["max_results"],
            collection_name=stats["collection_name"],
            endee_url=stats.get("endee_url"),
            ticket_count=stats["ticket_count"]
        )
        
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stats: {str(e)}"
        )

@router.post("/initialize")
async def initialize_system(assistant: SupportAssistant = Depends(get_assistant)):
    
    try:
        logger.info("🔄 API Initialize requested")
        
        success = assistant.initialize()
        
        if success:
            stats = assistant.get_stats()
            return {
                "success": True,
                "message": "System initialized successfully",
                "stats": stats
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize system"
            )
            
    except Exception as e:
        logger.error(f"❌ Initialize error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Initialization error: {str(e)}"
        )

@router.get("/search/{query}")
async def search_tickets(
    query: str,
    max_results: int = 5,
    assistant: SupportAssistant = Depends(get_assistant)
):
    
    try:
        
        query_embedding = assistant.embedding_service.generate_embedding(query)
        
        if query_embedding is None:
            raise HTTPException(status_code=500, detail="Failed to generate embedding")
        
        
        similar_tickets = assistant.vector_store.search_similar(query_embedding, max_results)
        
        return {
            "query": query,
            "embedding_dimension": len(query_embedding),
            "results_count": len(similar_tickets),
            "similar_tickets": similar_tickets
        }
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )

@router.get("/")
async def api_root():
    
    return {
        "message": "AI Support Assistant API",
        "version": "1.0.0",
        "powered_by": "Endee Vector Database",
        "endpoints": {
            "query": "POST /query - Submit support queries",
            "tickets": "POST /tickets - Batch insert tickets",
            "health": "GET /health - System health check",
            "stats": "GET /stats - System statistics",
            "initialize": "POST /initialize - Initialize system",
            "search": "GET /search/{query} - Direct vector search"
        },
        "documentation": "/docs"
    }
