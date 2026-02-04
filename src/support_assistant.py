"""
AI-Powered Support Assistant
Main orchestrator class that coordinates embeddings, vector search, and response generation
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from datetime import datetime

from .embeddings.embedding_service import EmbeddingService
from .vector_store.endee_client import EndeeClient
from .vector_store.local_vector_store import LocalVectorStore
from .llm.conversational_llm import ConversationalLLM
from config import config

logger = logging.getLogger(__name__)

class SupportAssistant:
    """Main class that orchestrates the AI-powered support assistant with Endee integration."""
    
    def __init__(self):
        """Initialize the support assistant with Endee vector database."""
        logger.info("🤖 Initializing AI Support Assistant...")
        
        # Initialize embedding service
        self.embedding_service = EmbeddingService()
        
        # Try to connect to Endee first, fallback to local storage
        self.endee_client = EndeeClient()
        
        if self.endee_client.health_check():
            logger.info("✅ Connected to Endee vector database")
            self.vector_store = self.endee_client
            self.using_endee = True
        else:
            logger.warning("⚠️  Endee not available, using local vector storage")
            self.vector_store = LocalVectorStore(config.ENDEE_COLLECTION_NAME)
            self.using_endee = False
        
        # Initialize conversational AI
        self.response_generator = ConversationalLLM()
        
        self._initialized = False
        self._ticket_count = 0
    
    def initialize(self) -> bool:
        """Initialize the system by setting up collections and loading sample data."""
        try:
            logger.info("🚀 Initializing support assistant system...")
            
            if self.using_endee:
                # Setup Endee collection
                if not self._setup_endee_collection():
                    logger.error("❌ Failed to setup Endee collection")
                    return False
            
            # Load sample support tickets
            self._load_sample_data()
            
            self._initialized = True
            logger.info("✅ Support assistant initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def _setup_endee_collection(self) -> bool:
        """Setup Endee collection with proper configuration."""
        try:
            collection_exists = self.vector_store.collection_exists()
            
            if not collection_exists:
                logger.info("🔧 Creating Endee collection...")
                dimension = self.embedding_service.dimension
                success = self.vector_store.create_collection(dimension)
                
                if success:
                    logger.info(f"✅ Created collection '{config.ENDEE_COLLECTION_NAME}' with dimension {dimension}")
                    return True
                else:
                    logger.error("❌ Failed to create Endee collection")
                    return False
            else:
                logger.info(f"✅ Collection '{config.ENDEE_COLLECTION_NAME}' already exists")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error setting up Endee collection: {e}")
            return False
    
    def handle_query(self, query: str, category: Optional[str] = None, 
                    max_results: int = None, conversation_id: str = "default") -> Dict[str, Any]:
        """
        Handle a support query using semantic search and AI response generation.
        
        Args:
            query: User's support query
            category: Optional category filter
            max_results: Maximum number of similar tickets to retrieve
            conversation_id: Unique conversation identifier
            
        Returns:
            Dictionary containing action, response, confidence, and similar tickets
        """
        if not self._initialized:
            logger.warning("System not initialized, attempting to initialize...")
            self.initialize()
        
        if max_results is None:
            max_results = config.MAX_RESULTS
        
        start_time = datetime.now()
        
        try:
            logger.info(f"🔍 Processing query: '{query[:50]}...' (conversation: {conversation_id})")
            
            # Generate embedding for the query
            query_text = f"{query} {category or ''}".strip()
            query_embedding = self.embedding_service.generate_embedding(query_text)
            
            if query_embedding is None:
                raise Exception("Failed to generate query embedding")
            
            # Search for similar tickets using Endee
            similar_tickets = self.vector_store.search_similar(query_embedding, max_results)
            
            # Filter by similarity threshold
            filtered_tickets = [
                ticket for ticket in similar_tickets 
                if ticket.get("score", 0) >= config.SIMILARITY_THRESHOLD
            ]
            
            logger.info(f"📊 Found {len(similar_tickets)} similar tickets, {len(filtered_tickets)} above threshold")
            
            # Generate intelligent response
            response = self.response_generator.generate_response(
                query, filtered_tickets, conversation_id
            )
            
            # Add processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            response["processing_time"] = processing_time
            
            logger.info(f"✅ Query processed in {processing_time:.3f}s - Action: {response['action']}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error handling query: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "action": "escalation",
                "response": "I apologize, but I'm experiencing technical difficulties. Please contact our support team for immediate assistance.",
                "confidence": 0.0,
                "similar_tickets": [],
                "processing_time": processing_time,
                "error": str(e)
            }
    
    def add_ticket(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Add a new support ticket to the vector database.
        
        Args:
            ticket_data: Dictionary containing ticket information
            
        Returns:
            Boolean indicating success
        """
        try:
            # Generate unique ID if not provided
            ticket_id = ticket_data.get("id", f"ticket_{uuid.uuid4().hex[:8]}")
            
            # Generate embedding for the ticket
            embedding = self.embedding_service.embed_support_ticket(
                title=ticket_data.get("title", ""),
                description=ticket_data.get("description", ""),
                category=ticket_data.get("category", "")
            )
            
            if embedding is None:
                logger.error(f"❌ Failed to generate embedding for ticket {ticket_id}")
                return False
            
            # Prepare metadata
            metadata = {
                "title": ticket_data.get("title", ""),
                "description": ticket_data.get("description", ""),
                "category": ticket_data.get("category", ""),
                "status": ticket_data.get("status", "open"),
                "resolution": ticket_data.get("resolution", ""),
                "priority": ticket_data.get("priority", "medium"),
                "created_at": ticket_data.get("created_at", datetime.now().isoformat()),
                "resolved_at": ticket_data.get("resolved_at", "")
            }
            
            # Insert into vector database
            success = self.vector_store.insert_vector(ticket_id, embedding, metadata)
            
            if success:
                self._ticket_count += 1
                logger.info(f"✅ Added ticket: {metadata['title']}")
            else:
                logger.error(f"❌ Failed to add ticket: {metadata['title']}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error adding ticket: {e}")
            return False
    
    def add_tickets_batch(self, tickets: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Add multiple tickets in batch for better performance.
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failed_count = 0
        
        logger.info(f"📦 Processing batch of {len(tickets)} tickets...")
        
        for ticket in tickets:
            if self.add_ticket(ticket):
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(f"📊 Batch complete: {success_count} successful, {failed_count} failed")
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "total": len(tickets)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            "initialized": self._initialized,
            "using_endee": self.using_endee,
            "vector_store": "Endee" if self.using_endee else "Local",
            "embedding_model": config.EMBEDDING_MODEL,
            "embedding_dimension": getattr(self.embedding_service, 'dimension', 384),
            "similarity_threshold": config.SIMILARITY_THRESHOLD,
            "max_results": config.MAX_RESULTS,
            "collection_name": config.ENDEE_COLLECTION_NAME,
            "endee_url": config.ENDEE_URL if self.using_endee else None,
            "ticket_count": self._ticket_count
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "system_initialized": self._initialized,
            "embedding_service": True,
            "vector_store_connected": False,
            "endee_available": False
        }
        
        try:
            # Check vector store connection
            if self.using_endee:
                health_status["endee_available"] = self.endee_client.health_check()
                health_status["vector_store_connected"] = health_status["endee_available"]
            else:
                health_status["vector_store_connected"] = True
            
            # Test embedding generation
            test_embedding = self.embedding_service.generate_embedding("test query")
            health_status["embedding_service"] = test_embedding is not None
            
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            health_status["error"] = str(e)
        
        return health_status
    
    def _load_sample_data(self):
        """Load sample support tickets for demonstration."""
        logger.info("📝 Loading sample support tickets...")
        
        sample_tickets = [
            {
                "id": "ticket_001",
                "title": "Cannot login to account",
                "description": "User is unable to login with correct credentials. Getting 'invalid password' error message.",
                "category": "authentication",
                "status": "resolved",
                "resolution": "Password reset required. User had caps lock enabled and was entering incorrect password.",
                "priority": "high"
            },
            {
                "id": "ticket_002", 
                "title": "Forgot password",
                "description": "User forgot their password and needs to reset it to access their account.",
                "category": "authentication",
                "status": "resolved",
                "resolution": "Sent password reset link to registered email address. User successfully reset password.",
                "priority": "medium"
            },
            {
                "id": "ticket_003",
                "title": "Payment failed during checkout",
                "description": "Credit card payment is being declined during checkout process. User has sufficient funds.",
                "category": "billing",
                "status": "resolved", 
                "resolution": "Issue with payment processor. User switched to different payment method and transaction succeeded.",
                "priority": "high"
            },
            {
                "id": "ticket_004",
                "title": "Mobile app crashes on startup",
                "description": "Mobile application crashes immediately after opening on iOS device. No error message displayed.",
                "category": "technical",
                "status": "resolved",
                "resolution": "App update required. User updated to latest version from App Store and issue resolved.",
                "priority": "high"
            },
            {
                "id": "ticket_005",
                "title": "Website loading very slowly",
                "description": "Website pages are loading very slowly, taking over 30 seconds to load completely.",
                "category": "performance",
                "status": "resolved",
                "resolution": "Server optimization performed and CDN cache cleared. Loading times improved significantly.",
                "priority": "medium"
            },
            {
                "id": "ticket_006",
                "title": "Autopay subscription failed",
                "description": "Automatic payment failed for monthly subscription. Card was charged but service not renewed.",
                "category": "autopay",
                "status": "resolved",
                "resolution": "Payment processor delay caused sync issue. Service manually renewed and duplicate charge refunded.",
                "priority": "high"
            },
            {
                "id": "ticket_007",
                "title": "Cannot setup automatic payments",
                "description": "User unable to set up automatic payments. Getting error when trying to save payment method.",
                "category": "autopay",
                "status": "resolved",
                "resolution": "Browser cache issue preventing form submission. Cleared cookies and successfully set up autopay.",
                "priority": "medium"
            },
            {
                "id": "ticket_008",
                "title": "Recurring payment declined by bank",
                "description": "Monthly autopay was declined by bank even though card has sufficient funds available.",
                "category": "autopay",
                "status": "resolved",
                "resolution": "Bank flagged recurring payment as suspicious transaction. User contacted bank to whitelist merchant.",
                "priority": "high"
            }
        ]
        
        # Add sample tickets to the database
        results = self.add_tickets_batch(sample_tickets)
        logger.info(f"📊 Sample data loaded: {results['success_count']} tickets added successfully")
        
        return results