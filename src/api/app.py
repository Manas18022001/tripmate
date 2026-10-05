import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import trips
from src.db.engine import engine, Base
from src.api.errors import TripMateError, tripmate_error_handler, generic_error_handler
from src.logging_config import setup_logging, get_logger

# Initialize structured logging
setup_logging()
logger = get_logger("app")

# Optional: Enable LangSmith tracing if the env var is set
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", "tripmate")
    logger.info("LangSmith tracing ENABLED (project: tripmate)")
else:
    logger.info("LangSmith tracing disabled (set LANGCHAIN_API_KEY to enable)")

# Enable LLM response caching via SQLite
from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache

cache_path = ".langchain_cache.db"
set_llm_cache(SQLiteCache(database_path=cache_path))
logger.info(f"LLM response cache enabled at {cache_path}")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TripMate API",
    description="AI-powered trip planning assistant",
    version="1.0.0",
)

# Register custom error handlers
app.add_exception_handler(TripMateError, tripmate_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

logger.info("TripMate API initialized successfully")
