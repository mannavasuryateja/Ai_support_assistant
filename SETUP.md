# 🚀 AI Support Assistant Setup Guide

## Quick Start (Demo Mode)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-support-assistant.git
cd ai-support-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python demo_app.py

# 4. Open your browser
# Visit: http://localhost:8000
```

## 🎯 What You'll Get

- ✅ **Semantic Search**: AI-powered ticket matching
- ✅ **Vector Database**: Endee integration with local fallback
- ✅ **Conversational AI**: Context-aware responses
- ✅ **Modern UI**: Beautiful chat interface
- ✅ **REST API**: Complete FastAPI endpoints
- ✅ **Production Ready**: Docker support included

## 🔧 Configuration Options

### Demo Mode (Default)
Works immediately without any setup - uses local TF-IDF embeddings.

### Production Mode (With Endee)
1. Get Endee API key from https://endee.io
2. Copy `.env.example` to `.env`
3. Add your Endee credentials
4. Run `python app.py`

## 📊 Features Demonstrated

- **Semantic Vector Search** using Endee vector database
- **Retrieval Augmented Generation (RAG)** for support
- **Intelligent Response Classification** (Solution/Clarification/Escalation)
- **Conversation Context Management**
- **Confidence Scoring** and similarity metrics
- **Fallback Architecture** for high availability

## 🎓 Perfect for Academic Projects

This project demonstrates:
- Modern AI/ML techniques
- Production-ready architecture
- Comprehensive documentation
- Real-world use case implementation
- Vector database integration
- Semantic search applications

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: See README.md
- **API Docs**: http://localhost:8000/docs (when running)