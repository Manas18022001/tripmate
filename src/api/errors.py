"""Custom exception classes and FastAPI exception handlers for TripMate."""

from fastapi import Request
from fastapi.responses import JSONResponse
from src.logging_config import get_logger

logger = get_logger("errors")


class TripMateError(Exception):
    """Base exception for all TripMate errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class LLMConnectionError(TripMateError):
    """Raised when the LLM (Ollama) is unreachable."""
    def __init__(self, message: str = "Cannot connect to Ollama. Make sure Ollama is running (ollama serve)."):
        super().__init__(message, status_code=503)


class LLMOutputError(TripMateError):
    """Raised when the LLM returns unparseable or invalid output."""
    def __init__(self, message: str = "The AI returned an invalid response. Please try again."):
        super().__init__(message, status_code=502)


class RAGDatabaseError(TripMateError):
    """Raised when the FAISS vector database cannot be loaded."""
    def __init__(self, message: str = "Knowledge base is unavailable. Please run the indexer."):
        super().__init__(message, status_code=503)


class TripNotFoundError(TripMateError):
    """Raised when a trip ID does not exist."""
    def __init__(self, trip_id: int):
        super().__init__(f"Trip with ID {trip_id} not found.", status_code=404)


# --- FastAPI Exception Handlers ---

async def tripmate_error_handler(request: Request, exc: TripMateError) -> JSONResponse:
    """Handle all custom TripMate exceptions."""
    logger.error(f"{exc.__class__.__name__}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_type": exc.__class__.__name__},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions to prevent 500 stack traces leaking to users."""
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again.", "error_type": "InternalError"},
    )
