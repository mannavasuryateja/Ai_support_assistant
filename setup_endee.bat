@echo off
echo 🚀 Setting up Endee Vector Database for AI Support Assistant
echo ============================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

echo ✅ Docker found

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Create data directory for Endee
if not exist "endee_data" mkdir endee_data
echo ✅ Created Endee data directory

REM Pull and run Endee container
echo 📦 Pulling Endee Docker image...
docker pull endee/endee:latest

echo 🚀 Starting Endee vector database...
docker run -d --name endee-support-db -p 8080:8080 -v %cd%/endee_data:/data -e NDD_AUTH_TOKEN= endee/endee:latest

REM Wait for Endee to start
echo ⏳ Waiting for Endee to start...
timeout /t 10 /nobreak >nul

REM Check if Endee is running
curl -s http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Endee is running successfully!
    echo 🌐 Endee URL: http://localhost:8080
    echo.
    echo Next steps:
    echo 1. Install Python dependencies: pip install -r requirements.txt
    echo 2. Run the application: python conversational_server.py
    echo 3. Open your browser: http://localhost:8000
) else (
    echo ❌ Endee failed to start. Check Docker logs:
    echo docker logs endee-support-db
)

echo.
echo To stop Endee: docker stop endee-support-db
echo To restart Endee: docker start endee-support-db
pause