# Deployment Guide

## Quick Deploy with Docker

```bash
# 1. Clone repository
git clone <your-repo-url>
cd ai-support-assistant

# 2. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Deploy with Docker Compose
docker-compose up -d
```

## Manual Deployment

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
python scripts/setup.py

# 3. Start application
python main.py
```

## Production Considerations

- Use environment variables for sensitive data
- Set up proper logging and monitoring
- Configure reverse proxy (nginx/Apache)
- Use production WSGI server (gunicorn)
- Set up SSL certificates
- Configure backup for vector database

## Environment Variables

Required:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ENDEE_URL`: Endee vector database URL
- `ENDEE_API_KEY`: Endee authentication key

Optional:
- `EMBEDDING_MODEL`: Sentence transformer model
- `SIMILARITY_THRESHOLD`: Minimum similarity score
- `MAX_RESULTS`: Maximum search results