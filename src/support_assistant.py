

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
    
    def __init__(self):
        logger.info("🤖 Initializing AI Support Assistant...")

        self.embedding_service = EmbeddingService()
        endee = EndeeClient()
        if endee.health_check():
            logger.info("✅ Connected to Endee vector database")
            self.vector_store = endee
            self.using_endee  = True
        else:
            logger.warning(
                "⚠️  Endee unavailable — falling back to LocalVectorStore"
            )
            self.vector_store = LocalVectorStore(config.ENDEE_COLLECTION_NAME)
            self.using_endee  = False

        
        self._endee_client = endee

        
        self.response_generator = ConversationalLLM()

        self._initialized  = False
        self._ticket_count = 0

    def initialize(self) -> bool:
        
        try:
            logger.info("🚀 Initializing support assistant system...")

            if not self._ensure_collection():
                logger.error("❌ Failed to set up vector store collection")
                return False

            self._load_sample_data()
            self._initialized = True
            logger.info("✅ Support assistant initialized successfully!")
            return True

        except Exception as e:
            logger.error("❌ Initialization failed: %s", e)
            return False

    def _ensure_collection(self) -> bool:
        
        try:
            if not self.vector_store.collection_exists():
                logger.info("🔧 Creating collection '%s'…", config.ENDEE_COLLECTION_NAME)
                dim = self.embedding_service.dimension
                ok  = self.vector_store.create_collection(dim)
                if not ok:
                    return False
                logger.info(
                    "✅ Collection '%s' created (dim=%d)",
                    config.ENDEE_COLLECTION_NAME, dim
                )
            else:
                logger.info("✅ Collection '%s' already exists", config.ENDEE_COLLECTION_NAME)
            return True

        except Exception as e:
            logger.error("❌ _ensure_collection error: %s", e)
            return False

    

    def handle_query(self, query: str, category: Optional[str] = None,
                     max_results: int = None,
                     conversation_id: str = "default") -> Dict[str, Any]:
        if not self._initialized:
            logger.warning("System not initialized — attempting init now…")
            self.initialize()

        if max_results is None:
            max_results = config.MAX_RESULTS

        start_time = datetime.now()

        try:
            logger.info("🔍 Query: '%s…' (conv=%s)", query[:50], conversation_id)

            query_text      = f"{query} {category or ''}".strip()
            query_embedding = self.embedding_service.generate_embedding(query_text)

            if query_embedding is None:
                raise RuntimeError("Failed to generate query embedding")

            similar_tickets = self.vector_store.search_similar(
                query_embedding, max_results
            )

            filtered_tickets = [
                t for t in similar_tickets
                if t.get("score", 0) >= config.SIMILARITY_THRESHOLD
            ]

            logger.info(
                "📊 %d similar tickets found, %d above threshold",
                len(similar_tickets), len(filtered_tickets)
            )

            response = self.response_generator.generate_response(
                query, filtered_tickets, conversation_id
            )

            processing_time = (datetime.now() - start_time).total_seconds()
            response["processing_time"] = processing_time

            logger.info(
                "✅ Query done in %.3fs — action: %s",
                processing_time, response["action"]
            )
            return response

        except Exception as e:
            logger.error("❌ handle_query error: %s", e)
            processing_time = (datetime.now() - start_time).total_seconds()
            return {
                "action":          "escalation",
                "response":        (
                    "I apologize, but I'm experiencing technical difficulties. "
                    "Please contact our support team for immediate assistance."
                ),
                "confidence":      0.0,
                "similar_tickets": [],
                "processing_time": processing_time,
                "error":           str(e),
            }

    # -------------------------------------------------------------- write

    def add_ticket(self, ticket_data: Dict[str, Any]) -> bool:
        try:
            ticket_id = ticket_data.get("id", f"ticket_{uuid.uuid4().hex[:8]}")

            embedding = self.embedding_service.embed_support_ticket(
                title       = ticket_data.get("title", ""),
                description = ticket_data.get("description", ""),
                category    = ticket_data.get("category", ""),
            )

            if embedding is None:
                logger.error("❌ No embedding for ticket %s", ticket_id)
                return False

            metadata = {
                "title":       ticket_data.get("title", ""),
                "description": ticket_data.get("description", ""),
                "category":    ticket_data.get("category", ""),
                "status":      ticket_data.get("status", "open"),
                "resolution":  ticket_data.get("resolution", ""),
                "priority":    ticket_data.get("priority", "medium"),
                "created_at":  ticket_data.get("created_at", datetime.now().isoformat()),
                "resolved_at": ticket_data.get("resolved_at", ""),
            }

            success = self.vector_store.insert_vector(ticket_id, embedding, metadata)

            if success:
                self._ticket_count += 1
                logger.info("✅ Added ticket: %s", metadata["title"])
            else:
                logger.error("❌ Failed to add ticket: %s", metadata["title"])

            return success

        except Exception as e:
            logger.error("❌ add_ticket error: %s", e)
            return False

    def add_tickets_batch(self, tickets: List[Dict[str, Any]]) -> Dict[str, int]:
        logger.info("📦 Processing batch of %d tickets…", len(tickets))
        success_count = 0
        failed_count  = 0

        for ticket in tickets:
            if self.add_ticket(ticket):
                success_count += 1
            else:
                failed_count += 1

        logger.info(
            "📊 Batch done: %d ok, %d failed", success_count, failed_count
        )
        return {
            "success_count": success_count,
            "failed_count":  failed_count,
            "total":         len(tickets),
        }

    # -------------------------------------------------------------- stats

    def get_stats(self) -> Dict[str, Any]:
        return {
            "initialized":        self._initialized,
            "using_endee":        self.using_endee,
            "vector_store":       "Endee" if self.using_endee else "LocalVectorStore",
            "embedding_model":    config.EMBEDDING_MODEL,
            "embedding_dimension": getattr(self.embedding_service, "dimension", 384),
            "similarity_threshold": config.SIMILARITY_THRESHOLD,
            "max_results":        config.MAX_RESULTS,
            "collection_name":    config.ENDEE_COLLECTION_NAME,
            "endee_url":          config.ENDEE_URL if self.using_endee else None,
            "ticket_count":       self._ticket_count,
        }

    def health_check(self) -> Dict[str, Any]:
        status = {
            "system_initialized":   self._initialized,
            "embedding_service":    False,
            "vector_store_connected": False,
            "endee_available":      False,
        }
        try:
            if self.using_endee:
                endee_ok = self._endee_client.health_check()
                status["endee_available"]       = endee_ok
                status["vector_store_connected"] = endee_ok
            else:
                # LocalVectorStore is always "connected"
                status["vector_store_connected"] = True

            test_emb = self.embedding_service.generate_embedding("test")
            status["embedding_service"] = test_emb is not None

        except Exception as e:
            logger.error("❌ health_check error: %s", e)
            status["error"] = str(e)

        return status

    # --------------------------------------------------------- sample data

    def _load_sample_data(self):
        logger.info("📝 Loading sample support tickets…")

        sample_tickets = [
            {
                "id": "ticket_001",
                "title": "Cannot login to account",
                "description": "User is unable to login with correct credentials. Getting 'invalid password' error message.",
                "category": "authentication",
                "status": "resolved",
                "resolution": "Password reset required. User had caps lock enabled and was entering incorrect password.",
                "priority": "high",
            },
            {
                "id": "ticket_002",
                "title": "Forgot password",
                "description": "User forgot their password and needs to reset it to access their account.",
                "category": "authentication",
                "status": "resolved",
                "resolution": "Sent password reset link to registered email address. User successfully reset password.",
                "priority": "medium",
            },
            {
                "id": "ticket_003",
                "title": "Payment failed during checkout",
                "description": "Credit card payment is being declined during checkout process. User has sufficient funds.",
                "category": "billing",
                "status": "resolved",
                "resolution": "Issue with payment processor. User switched to different payment method and transaction succeeded.",
                "priority": "high",
            },
            {
                "id": "ticket_004",
                "title": "Mobile app crashes on startup",
                "description": "Mobile application crashes immediately after opening on iOS device. No error message displayed.",
                "category": "technical",
                "status": "resolved",
                "resolution": "App update required. User updated to latest version from App Store and issue resolved.",
                "priority": "high",
            },
            {
                "id": "ticket_005",
                "title": "Website loading very slowly",
                "description": "Website pages are loading very slowly, taking over 30 seconds to load completely.",
                "category": "performance",
                "status": "resolved",
                "resolution": "Server optimization performed and CDN cache cleared. Loading times improved significantly.",
                "priority": "medium",
            },
            {
                "id": "ticket_006",
                "title": "Autopay subscription failed",
                "description": "Automatic payment failed for monthly subscription. Card was charged but service not renewed.",
                "category": "autopay",
                "status": "resolved",
                "resolution": "Payment processor delay caused sync issue. Service manually renewed and duplicate charge refunded.",
                "priority": "high",
            },
            {
                "id": "ticket_007",
                "title": "Cannot setup automatic payments",
                "description": "User unable to set up automatic payments. Getting error when trying to save payment method.",
                "category": "autopay",
                "status": "resolved",
                "resolution": "Browser cache issue preventing form submission. Cleared cookies and successfully set up autopay.",
                "priority": "medium",
            },
            {
                "id": "ticket_008",
                "title": "Recurring payment declined by bank",
                "description": "Monthly autopay was declined by bank even though card has sufficient funds available.",
                "category": "autopay",
                "status": "resolved",
                "resolution": "Bank flagged recurring payment as suspicious transaction. User contacted bank to whitelist merchant.",
                "priority": "high",
            },
        ]

        results = self.add_tickets_batch(sample_tickets)
        logger.info(
            "📊 Sample data loaded: %d/%d tickets inserted",
            results["success_count"], results["total"]
        )
        return results
