import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Endee Configuration
    ENDEE_URL = os.getenv("ENDEE_URL", "http://localhost:8080")
    ENDEE_API_KEY = os.getenv("ENDEE_API_KEY", "")
    ENDEE_COLLECTION_NAME = os.getenv("ENDEE_COLLECTION_NAME", "support_tickets")
    
    # Embedding Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Search Configuration
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", "5"))
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

config = Config()