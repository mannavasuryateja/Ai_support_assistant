#!/usr/bin/env python3
"""
Setup script for the AI-Powered Support Assistant.
This script helps with initial setup and configuration.
"""

import os
import sys
import json
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✓ Created .env file from template")
        print("  Please edit .env file with your API keys and configuration")
        return True
    elif env_file.exists():
        print("✓ .env file already exists")
        return True
    else:
        print("✗ .env.example file not found")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "python-dotenv",
        "openai",
        "sentence-transformers",
        "numpy",
        "pandas",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("✗ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("✓ All required packages are installed")
        return True

def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "logs",
        "examples",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def validate_config():
    """Validate configuration settings."""
    try:
        from config import config
        
        print("✓ Configuration loaded successfully")
        
        # Check critical settings
        if not config.OPENAI_API_KEY:
            print("⚠ Warning: OPENAI_API_KEY not set")
        
        if not config.ENDEE_URL:
            print("⚠ Warning: ENDEE_URL not set")
        
        print(f"  - Embedding model: {config.EMBEDDING_MODEL}")
        print(f"  - LLM model: {config.LLM_MODEL}")
        print(f"  - Endee URL: {config.ENDEE_URL}")
        print(f"  - Collection name: {config.ENDEE_COLLECTION_NAME}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_imports():
    """Test if all modules can be imported."""
    try:
        from src.support_assistant import SupportAssistant
        from src.embeddings.embedding_service import EmbeddingService
        from src.vector_store.endee_client import EndeeClient
        from src.llm.response_generator import ResponseGenerator
        
        print("✓ All modules imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Run the setup process."""
    print("AI-Powered Support Assistant Setup")
    print("=" * 40)
    
    success = True
    
    # Create directories
    print("\n1. Creating directories...")
    create_directories()
    
    # Create .env file
    print("\n2. Setting up environment file...")
    if not create_env_file():
        success = False
    
    # Check dependencies
    print("\n3. Checking dependencies...")
    if not check_dependencies():
        success = False
    
    # Test imports
    print("\n4. Testing module imports...")
    if not test_imports():
        success = False
    
    # Validate configuration
    print("\n5. Validating configuration...")
    if not validate_config():
        success = False
    
    print("\n" + "=" * 40)
    
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your API keys")
        print("2. Start Endee vector database")
        print("3. Run: python main.py")
        print("4. Visit: http://localhost:8000/docs")
    else:
        print("✗ Setup completed with errors")
        print("Please fix the issues above before running the application")
        sys.exit(1)

if __name__ == "__main__":
    main()