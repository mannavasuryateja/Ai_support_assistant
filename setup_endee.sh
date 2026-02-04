#!/bin/bash

echo "🚀 Setting up Endee Vector Database for AI Support Assistant"
echo "============================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker found"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Create data directory for Endee
mkdir -p endee_data
echo "✅ Created Endee data directory"

# Pull and run Endee container
echo "📦 Pulling Endee Docker image..."
docker pull endee/endee:latest

echo "🚀 Starting Endee vector database..."
docker run -d \
    --name endee-support-db \
    -p 8080:8080 \
    -v $(pwd)/endee_data:/data \
    -e NDD_AUTH_TOKEN= \
    endee/endee:latest

# Wait for Endee to start
echo "⏳ Waiting for Endee to start..."
sleep 10

# Check if Endee is running
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Endee is running successfully!"
    echo "🌐 Endee URL: http://localhost:8080"
    echo ""
    echo "Next steps:"
    echo "1. Install Python dependencies: pip install -r requirements.txt"
    echo "2. Run the application: python conversational_server.py"
    echo "3. Open your browser: http://localhost:8000"
else
    echo "❌ Endee failed to start. Check Docker logs:"
    echo "docker logs endee-support-db"
fi

echo ""
echo "To stop Endee: docker stop endee-support-db"
echo "To restart Endee: docker start endee-support-db"