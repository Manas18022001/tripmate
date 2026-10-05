# 🗺️ TripMate — AI-Powered Trip Planning Assistant

An intelligent, multi-agent trip planning system built with **LangGraph**, **FastAPI**, **Streamlit**, and **RAG** (Retrieval-Augmented Generation). TripMate generates personalized, budget-aware itineraries for Indian destinations using a team of AI agents that research, plan, and optimize your trip.

## ✨ Features

- **Multi-Agent Architecture:** A Supervisor agent orchestrates specialized Research, Itinerary, and Budget agents using LangGraph
- **RAG Pipeline:** Curated destination knowledge base with FAISS vector search and local embeddings
- **Conversational Refinement:** Chat with the AI to modify your itinerary after generation
- **Budget Optimization:** Automatic budget checking with re-planning loop if costs exceed limits
- **Trip Persistence:** Save, view, and delete trips with SQLite
- **Dual LLM Support:** Works with local Ollama (offline) or Google Gemini (cloud)
- **LLM Response Caching:** Identical queries return instantly from cache
- **Dockerized:** One-command deployment with Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────────────────────┐
│   Streamlit UI  │────▶│         FastAPI Backend           │
│   (Port 8501)   │     │         (Port 8000)               │
└─────────────────┘     └──────────┬───────────────────────┘
                                   │
                        ┌──────────▼───────────────────────┐
                        │     LangGraph Multi-Agent        │
                        │                                   │
                        │  Supervisor ──▶ Research Agent     │
                        │      │              │             │
                        │      ▼              ▼             │
                        │  Itinerary    FAISS + RAG         │
                        │  Agent        (Local Embeddings)  │
                        │      │                            │
                        │      ▼                            │
                        │  Budget Agent                     │
                        └──────────┬───────────────────────┘
                                   │
                        ┌──────────▼───────────────────────┐
                        │   Ollama (Local LLM)              │
                        │   or Google Gemini (Cloud)        │
                        └──────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Ollama](https://ollama.com/) (for local LLM)

### 1. Clone & Install
```bash
git clone https://github.com/manas18022001/tripmate.git
cd tripmate
poetry install
```

### 2. Setup Ollama
```bash
ollama pull llama3.2
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (defaults work for Ollama)
```

### 4. Build the Knowledge Base
```bash
poetry run python src/rag/indexer.py
```

### 5. Run the App
```bash
# Terminal 1 — Backend
poetry run uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend
poetry run streamlit run src/ui/app.py --server.port 8501
```

Open http://localhost:8501 and start planning!

## 🐳 Docker

```bash
docker-compose up --build
```
This starts the FastAPI backend, Streamlit frontend, and Ollama service together.

## 🧪 Testing

```bash
poetry run pytest tests/ -v
```

## 📁 Project Structure

```
tripmate/
├── src/
│   ├── agents/          # LangGraph multi-agent system
│   │   ├── graph.py     # Agent workflow definition
│   │   ├── state.py     # Shared agent state
│   │   ├── supervisor.py
│   │   ├── research_agent.py
│   │   ├── itinerary_agent.py
│   │   ├── budget_agent.py
│   │   └── tools/       # Agent tools (RAG search, weather)
│   ├── api/             # FastAPI application
│   │   ├── app.py       # App factory with error handlers & caching
│   │   ├── errors.py    # Custom exception hierarchy
│   │   ├── routes/      # API endpoints
│   │   └── schemas/     # Pydantic models
│   ├── db/              # SQLAlchemy database layer
│   ├── rag/             # RAG pipeline (indexer, embeddings)
│   ├── ui/              # Streamlit frontend
│   └── config.py        # Pydantic settings
├── data/destinations/   # Curated travel knowledge base (markdown)
├── scripts/             # Utility scripts (scraper, cleaner)
├── tests/               # Automated test suite
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## 🔧 Configuration

| Variable | Default | Description |
|---|---|---|
| `LLM_MODEL` | `llama3.2` | Ollama model name or Gemini model |
| `GOOGLE_API_KEY` | `""` | Required only for Gemini |
| `DATABASE_URL` | `sqlite:///./tripmate.db` | Database connection string |
| `LANGCHAIN_API_KEY` | `""` | Optional: enables LangSmith tracing |

## 📜 License

MIT
