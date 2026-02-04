#!/usr/bin/env python3
"""
Quick setup script for AI Support Assistant.
This script sets up the system to work with or without Endee.
"""

import os
import sys
import subprocess
import requests
import time

def check_docker():
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is installed")
            
            # Check if Docker daemon is running
            result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker is running")
                return True
            else:
                print("⚠️  Docker is installed but not running")
                return False
        else:
            print("❌ Docker is not installed")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def setup_endee():
    """Set up Endee vector database using Docker."""
    print("\n🚀 Setting up Endee Vector Database...")
    
    try:
        # Create data directory
        os.makedirs("endee_data", exist_ok=True)
        print("✅ Created Endee data directory")
        
        # Check if Endee container already exists
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=endee-support-db'], 
                              capture_output=True, text=True)
        
        if 'endee-support-db' in result.stdout:
            print("🔄 Endee container already exists, starting it...")
            subprocess.run(['docker', 'start', 'endee-support-db'], check=True)
        else:
            print("📦 Pulling Endee Docker image...")
            subprocess.run(['docker', 'pull', 'endee/endee:latest'], check=True)
            
            print("🚀 Starting Endee container...")
            subprocess.run([
                'docker', 'run', '-d',
                '--name', 'endee-support-db',
                '-p', '8080:8080',
                '-v', f'{os.getcwd()}/endee_data:/data',
                '-e', 'NDD_AUTH_TOKEN=',
                'endee/endee:latest'
            ], check=True)
        
        # Wait for Endee to start
        print("⏳ Waiting for Endee to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:8080/health', timeout=2)
                if response.status_code == 200:
                    print("✅ Endee is running successfully!")
                    print("🌐 Endee URL: http://localhost:8080")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("⚠️  Endee may still be starting. Check with: docker logs endee-support-db")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set up Endee: {e}")
        return False
    except Exception as e:
        print(f"❌ Error setting up Endee: {e}")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file with default settings."""
    env_content = """# Endee Configuration
ENDEE_URL=http://localhost:8080
ENDEE_API_KEY=
ENDEE_COLLECTION_NAME=support_tickets

# Embedding Model Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Search Configuration
SIMILARITY_THRESHOLD=0.7
MAX_RESULTS=5

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function."""
    print("🤖 AI Support Assistant Setup")
    print("=" * 40)
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        return
    
    # Check Docker and setup Endee
    docker_available = check_docker()
    endee_running = False
    
    if docker_available:
        endee_running = setup_endee()
    else:
        print("\n⚠️  Docker not available. The system will run in demo mode.")
        print("   To use Endee later:")
        print("   1. Install Docker Desktop")
        print("   2. Run: python quick_setup.py")
    
    print("\n" + "=" * 40)
    print("🎉 Setup Complete!")
    print("\nSystem Status:")
    print(f"   Docker: {'✅ Available' if docker_available else '❌ Not available'}")
    print(f"   Endee:  {'✅ Running' if endee_running else '⚠️  Demo mode'}")
    print(f"   Dependencies: ✅ Installed")
    
    print("\n🚀 Next Steps:")
    print("   1. Run the application: python conversational_server.py")
    print("   2. Open your browser: http://localhost:8000")
    
    if not endee_running:
        print("\n💡 Note: System will use local vector storage (demo mode)")
        print("   This still demonstrates all the core functionality!")

if __name__ == "__main__":
    main()