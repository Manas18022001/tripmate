# 🗺️ TripMate — Implementation Plan

## Goal Description

Build **TripMate**, an AI-powered trip planning assistant that generates personalized, budget-aware itineraries for Indian destinations using a multi-agent architecture. The project progresses from basic to production-level across 4 phases, serving as a comprehensive learning project for LangChain, LangGraph, and RAG.

## Decisions Summary

| Decision | Choice |
|---|---|
| **Application Type** | FastAPI backend + Streamlit frontend |
| **AI Architecture** | Multi-agent system with LangGraph (Supervisor pattern) |
| **LLM** | Google Gemini (gemini-2.0-flash) |
| **Embedding Model** | Google text-embedding-004 (768 dims) |
| **Vector Database** | ChromaDB (local) |
| **Relational Database** | SQLite via SQLAlchemy (migratable to PostgreSQL) |
| **RAG Data Sources** | Travel guides + Weather API + Food/Restaurant data |
| **Core Features** | Smart itinerary, Budget optimization, Personalized recommendations |
| **User Interaction** | Structured form → AI generation → Conversational refinement |
| **Geographic Scope** | India-focused (50+ destinations) |
| **Dependency Management** | Poetry (Python 3.11+) |

---

## Tech Stack Overview

```
Frontend (Streamlit)
  ├── Trip Input Form
  ├── Chat Interface
  └── Itinerary Display
        │
API Layer (FastAPI)
  ├── REST Routes
  ├── WebSocket (Streaming)
  └── Session Management
        │
Agent Layer (LangGraph)
  ├── Supervisor Agent
  ├── Research Agent
  ├── Itinerary Agent
  └── Budget Agent
        │
RAG Pipeline
  ├── Document Loaders
  ├── Text Splitters
  ├── Google Embeddings
  ├── ChromaDB
  └── Retriever + Reranker
        │
Data Layer
  ├── SQLite (Users, Trips, Sessions)
  ├── OpenWeatherMap API
  └── Google Places API
```

---

## Complete Dependency List

```toml
[tool.poetry.dependencies]
python = "^3.11"

# Core AI/ML
langchain = "^0.3"
langchain-google-genai = "^2.0"
langchain-community = "^0.3"
langgraph = "^0.4"

# RAG & Vector Store
chromadb = "^0.5"

# Web Framework
fastapi = "^0.115"
uvicorn = {extras = ["standard"], version = "^0.30"}
streamlit = "^1.40"

# Database
sqlalchemy = "^2.0"
alembic = "^1.13"

# External APIs
httpx = "^0.27"
python-dotenv = "^1.0"

# Utilities
pydantic = "^2.9"
pydantic-settings = "^2.5"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3"
pytest-asyncio = "^0.24"
ruff = "^0.7"
pre-commit = "^4.0"
```

---

## Project Structure

```
tripmate/
├── pyproject.toml
├── poetry.lock
├── .env.example
├── .env                             # gitignored
├── .gitignore
├── README.md
├── docs/
│   ├── implementation_plan.md       # This file
│   └── decision_record.md
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
│
├── data/
│   ├── destinations/                # Markdown guides
│   │   ├── manali.md
│   │   ├── goa.md
│   │   └── ...
│   ├── food/
│   └── chroma_db/                   # ChromaDB storage
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── trips.py
│   │   │   ├── chat.py
│   │   │   └── health.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── trip.py
│   │   │   └── chat.py
│   │   └── dependencies.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── supervisor.py
│   │   ├── research_agent.py
│   │   ├── itinerary_agent.py
│   │   ├── budget_agent.py
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── weather.py
│   │       ├── places.py
│   │       └── search.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── indexer.py
│   │   ├── retriever.py
│   │   ├── embeddings.py
│   │   └── chunking.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   └── ui/
│       ├── app.py
│       ├── pages/
│       │   ├── 1_🏠_Home.py
│       │   ├── 2_🗺️_Plan_Trip.py
│       │   └── 3_📋_My_Trips.py
│       └── components/
│           ├── trip_form.py
│           ├── itinerary_display.py
│           └── chat_widget.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agents/
│   ├── test_rag/
│   └── test_api/
│
├── scripts/
│   ├── index_knowledge_base.py
│   └── seed_data.py
│
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

---

## Multi-Agent Architecture (LangGraph)

### Agent State Schema

```python
class TripState(MessagesState):
    # User input
    destination: str
    num_days: int
    budget: float           # in INR
    interests: list[str]
    num_travelers: int
    travel_month: str

    # Research agent output
    destination_info: str
    weather_info: str
    recommended_places: list[dict]

    # Itinerary agent output
    itinerary: list[dict]

    # Budget agent output
    budget_breakdown: dict
    budget_status: Literal["within_budget", "over_budget", "optimized"]

    # Supervisor control
    next_agent: str
    iteration_count: int
```

### Agent Graph Flow

```
[Start] → Supervisor
             ├── needs_research → Research Agent → Supervisor
             ├── needs_itinerary → Itinerary Agent → Supervisor
             ├── needs_budget → Budget Agent → Supervisor
             │                    ├── within_budget → Supervisor → FINISH
             │                    └── over_budget → Supervisor → Itinerary Agent (re-plan)
             └── plan_complete → [End]
```

### Supervisor Logic

```python
def supervisor(state: TripState) -> dict:
    if not state.get("destination_info"):
        return {"next_agent": "research"}
    if not state.get("itinerary"):
        return {"next_agent": "itinerary"}
    if not state.get("budget_breakdown"):
        return {"next_agent": "budget"}
    if state.get("budget_status") == "over_budget" and state["iteration_count"] < 3:
        return {"next_agent": "itinerary"}  # Re-plan with budget constraints
    return {"next_agent": "FINISH"}
```

---

## RAG Pipeline Design

### Knowledge Base Schema (per destination)

```markdown
# Destination Name, State
## Overview / Best Time to Visit / Top Attractions
## Budget Guide (₹ per person per day: budget/mid/luxury)
## Local Food / Getting There / Tips
```

### Chunking: `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)`

### Retrieval: Semantic search (top-k=5) + metadata filtering by destination + multi-query retrieval

---

## Phase Breakdown

### Phase 1 — Foundation (Week 1-2)
- Project setup (Poetry, directory structure, configs)
- Basic FastAPI with `/plan-trip` POST endpoint
- Simple LangChain chain (no agents) → generates basic itinerary
- Streamlit form + itinerary display
- SQLAlchemy models for Trip + basic CRUD

### Phase 2 — RAG + Multi-Agent (Week 3-4)
- 15-20 destination guides in markdown
- Full RAG pipeline: load → chunk → embed → ChromaDB
- LangGraph graph: Supervisor + Research + Itinerary + Budget agents
- Agent tools: weather lookup, RAG search, places search

### Phase 3 — Full Features (Week 5-6)
- Budget optimization with feedback loops
- Interest-based personalization
- WebSocket chat for plan refinement
- Trip persistence + LangGraph checkpointing

### Phase 4 — Production Hardening (Week 7-8)
- Error handling, retry logic, rate limiting, caching
- Structured logging + LangSmith tracing
- Unit + integration tests
- Docker + CI/CD (GitHub Actions)

---

## Prerequisites

1. **Google AI Studio API Key** (free) — [Get here](https://aistudio.google.com/apikey)
2. **OpenWeatherMap API Key** (free tier) — [Get here](https://openweathermap.org/api) — needed Phase 2
3. **Google Places API Key** (free tier) — needed Phase 2
4. **Poetry** — install via `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -`

## Verification

```bash
poetry run pytest tests/ -v           # Full test suite
# Phase-specific:
poetry run pytest tests/test_api/     # Phase 1
poetry run pytest tests/test_rag/     # Phase 2
poetry run pytest tests/test_agents/  # Phase 2-3
```

---

## Future Features Backlog

| Feature | Complexity | Target Phase |
|---|---|---|
| Packing list generator | Low | 5 |
| Local language essentials | Low | 5 |
| Trip comparison (side-by-side) | Medium | 5 |
| Export to PDF/calendar | Medium | 5 |
| Multi-city route optimization | High | 6 |
| Group trip planning | High | 6 |
| User authentication (JWT) | Medium | 6 |
| Global destinations | Medium | 6 |
| Real-time flight/hotel pricing | High | 7 |
| Collaborative trip editing | High | 7 |
