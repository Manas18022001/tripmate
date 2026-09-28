# 🧭 TripMate — Technical Decision Record

> Why we chose what we chose. Each decision includes the reasoning, rejected alternatives, and migration path.

---

## 1. FastAPI + Streamlit (over Django, React, CLI)

**Why FastAPI:**
- Async-native — critical for LLM streaming and concurrent API calls to weather/places services
- Auto-generates OpenAPI docs — instant Swagger UI for testing without Postman
- Pydantic-first — request/response validation is built-in, same library LangChain uses
- Lightweight — no ORM opinions, no template engine baggage; we pick our own tools

**Why Streamlit (not React/Next.js):**
- This is an AI/ML learning project, not a frontend project. Streamlit lets us build a functional UI in ~100 lines of Python
- Native support for chat interfaces, forms, and streaming — exactly what TripMate needs
- Same language (Python) top to bottom — no context-switching

**Why not Django:** Monolithic. Comes with an admin panel, template engine, and ORM we don't need. FastAPI is leaner and teaches modern API patterns (dependency injection, async/await).

**Migration path:** Streamlit → Next.js frontend when the AI layer is stable and we want a polished UI.

---

## 2. Multi-Agent with Supervisor Pattern (over single chain, sequential pipeline)

**Why multi-agent:**
- Trip planning is naturally decomposable — research, scheduling, and budgeting are distinct skills requiring different tools and prompts
- Enables **feedback loops** — budget agent can reject an itinerary and force re-planning, which a linear chain can't do
- Each agent is independently testable and improvable

**Why supervisor over other patterns:**

| Pattern | Rejected Because |
|---|---|
| Sequential pipeline | Can't loop. If budget fails, you'd need to restart from scratch |
| Peer-to-peer (collaborative) | No central control → infinite loops, contradictory outputs, impossible to debug |
| Hierarchical (multi-level supervisors) | Over-engineered for 3-4 agents. Adds latency and complexity with no benefit at this scale |

**Why supervisor works:** One orchestrator makes routing decisions based on state. It's deterministic, debuggable, and the most common pattern in production LangGraph apps.

---

## 3. Google Gemini 2.0 Flash (over GPT-4o, Groq, multi-LLM)

**Why Gemini:**
- **Free tier: 15 RPM, 1M tokens/day** — sufficient for development and light usage without spending a rupee
- Quality is competitive with GPT-4o-mini for structured generation tasks (itineraries, JSON output)
- Function calling support — essential for tool-using agents
- Same provider as our embedding model — one API key, one billing account

**Why not OpenAI:** Costs money from day 1. For a learning project, free > paid.

**Why not Groq:** Fast inference, but uses open-source models (Llama/Mixtral) which are weaker at structured JSON output and function calling — the core of our agent architecture.

**Why not multi-LLM:** Premature optimization. Multiple providers = multiple API keys, different response formats, harder debugging. Optimize model routing after the architecture works.

---

## 4. ChromaDB (over Pinecone, Weaviate, FAISS)

**Why ChromaDB:**
- Runs locally with zero infrastructure — `pip install chromadb` and done
- Persistent storage to disk — survives restarts (FAISS doesn't by default)
- Native LangChain integration with metadata filtering — filter chunks by destination
- Handles millions of documents — more than enough for our knowledge base

| Alternative | Rejected Because |
|---|---|
| Pinecone | Managed cloud service — requires account, has free tier limits, vendor lock-in. Unnecessary for local development |
| Weaviate | Powerful but heavy setup (Docker). Hybrid search is nice but overkill for our scale |
| FAISS | No persistence out of the box, no metadata filtering, more low-level plumbing needed |

**Migration path:** ChromaDB → Pinecone is a config change (`Chroma.from_documents` → `Pinecone.from_documents`), not a rewrite.

---

## 5. Google text-embedding-004 (over OpenAI, HuggingFace, Cohere)

**Why Google embeddings:**
- **Free** with the same Gemini API key — no additional cost or account
- 768-dimensional vectors — good balance of quality and storage efficiency
- Consistent ecosystem — Gemini LLM + Gemini embeddings eliminates cross-provider quirks

**Why not HuggingFace local models:** Batch indexing on CPU is noticeably slow. Cloud embeddings are faster and free — no reason to run locally.

**Why not OpenAI embeddings:** Costs money. Google's are free and comparable quality.

---

## 6. SQLite + SQLAlchemy (over PostgreSQL, MongoDB, no DB)

**Why SQLite:**
- Zero setup — it's a file. No Docker, no server process, no connection management
- Perfect for development and single-user usage
- Full SQL support for structured trip data (users, trips, itineraries)

**Why SQLAlchemy ORM:**
- Database-agnostic — same models work with SQLite, PostgreSQL, MySQL
- Alembic for migrations — proper schema evolution as features grow
- Teaches production data modeling patterns (relationships, indices, constraints)

**Why not MongoDB:** Trip data is relational (User → has many Trips → has many DayPlans). MongoDB's document model adds denormalization headaches without benefit. "Flexible schema" is a liability when your data has clear structure.

**Why not no database:** Losing all trips on restart is unacceptable even for a learning project. Persistence is table stakes.

**Migration path:** Change `sqlite:///./tripmate.db` to `postgresql://...` in `.env`. SQLAlchemy handles the rest.

---

## 7. Three RAG Data Sources (over single source)

**Why travel guides + weather + food (not just guides):**

| Source | What It Teaches | Value to User |
|---|---|---|
| **Travel guides** (curated markdown) | Document loading, chunking, embedding, semantic search | Destination knowledge |
| **Weather API** (OpenWeatherMap) | Tool-based retrieval, real-time data integration | "Don't visit Goa in monsoon" |
| **Food/restaurants** (Google Places) | API-based retrieval, structured data processing | Actionable dining recommendations |

**Why not single source:** A RAG system with one data type is just a chatbot with extra steps. Multiple sources teach **retriever fusion**, **source routing**, and **heterogeneous data handling** — the real production RAG skills.

**Why not flight/hotel APIs in v1:** Real-time pricing APIs have complex auth, rate limits, webhook callbacks, and caching requirements. They're an integration project, not an AI learning exercise. Deferred to future phases.

---

## 8. Structured Form + Chat Refinement (over pure chat, form-only)

**Why hybrid approach:**
- **Form captures structured input reliably** — destination, dates, budget don't need NLP extraction
- **Chat enables natural refinement** — "Make day 2 more relaxed" is easier to type than re-filling a form
- **Reduces LLM errors** — structured input means no parameter extraction failures

**Why not pure chat:** Users would need to type everything in natural language. The LLM would need to extract parameters (destination, dates, budget) from free text — adding an error-prone parsing step that's completely avoidable with a form.

---

## 9. India-Focused Scope (over global)

**Why India first:**
- **Quality over quantity** — deep knowledge for 50 destinations beats shallow coverage of 500 global cities
- **Evaluable** — you can personally judge if "Manali in October" recommendations are good; you can't easily verify "Dubrovnik in April"
- **Domain richness** — monsoon seasons, regional festivals, budget ranges in ₹, local transport quirks make India a non-trivial planning domain
- **RAG shines on depth** — with thin knowledge, the LLM just hallucates and RAG adds nothing

**Migration path:** Add `data/destinations/international/` folder, re-index. Architecture doesn't change.

---

## 10. Poetry (over pip, uv)

**Why Poetry:**
- Single tool for dependency resolution, virtual env, lock files, and project metadata
- `pyproject.toml` replaces `requirements.txt` + `setup.py` + `setup.cfg`
- Lock file ensures reproducible builds across machines
- Clear separation of direct vs. transitive dependencies

**Why not `pip + requirements.txt`:** `pip freeze` dumps 200+ transitive deps with no way to tell which you actually need. Version conflicts are silent until runtime. No lock file = "works on my machine" bugs.

**Why not `uv`:** Excellent tool but newer — fewer tutorials, less ecosystem maturity. Poetry is the safer bet for learning.

---

## 11. 4-Phase Incremental Build (over build-all-at-once)

**Why phased:**
- **Working app at every milestone** — Phase 1 alone produces a functional trip planner
- **Learning is layered** — you can't debug agent orchestration if you haven't understood chains first
- **Motivation sustains** — seeing results every 2 weeks prevents the "still setting up after 3 weeks" burnout
- **Clean git history** — each phase is a logical commit boundary

| Phase | What You Learn |
|---|---|
| 1 — Foundation | FastAPI, LangChain basics, project structure |
| 2 — RAG + Agents | Embeddings, vector search, LangGraph, multi-agent orchestration |
| 3 — Full Features | State management, WebSockets, complex workflows, persistence |
| 4 — Production | Error handling, testing, Docker, monitoring, CI/CD |
