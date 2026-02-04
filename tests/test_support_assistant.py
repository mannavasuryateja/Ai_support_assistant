import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.support_assistant import SupportAssistant

class TestSupportAssistant(unittest.TestCase):
    
    def setUp(self):
        self.assistant = SupportAssistant()
    
    @patch('src.support_assistant.EndeeClient')
    @patch('src.support_assistant.EmbeddingService')
    @patch('src.support_assistant.ResponseGenerator')
    def test_handle_query(self, mock_response_gen, mock_embedding, mock_endee):
        # Mock the services
        mock_embedding.return_value.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_endee.return_value.search_similar.return_value = [
            {"score": 0.8, "metadata": {"title": "Test", "description": "Test desc"}}
        ]
        mock_response_gen.return_value.generate_response.return_value = {
            "action": "solution",
            "response": "Test response",
            "confidence": 0.9,
            "similar_tickets": []
        }
        
        # Test query handling
        result = self.assistant.handle_query("test query")
        
        self.assertEqual(result["action"], "solution")
        self.assertEqual(result["response"], "Test response")
        self.assertEqual(result["confidence"], 0.9)
    
    def test_get_stats(self):
        stats = self.assistant.get_stats()
        
        self.assertIn("initialized", stats)
        self.assertIn("embedding_model", stats)
        self.assertIn("llm_model", stats)

if __name__ == '__main__':
    unittest.main()