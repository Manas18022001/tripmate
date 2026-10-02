from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM
    google_api_key: str = ""
    llm_model: str = "gemini-3.8-pro"
    llm_temperature: float = 0.7
    
    # Database
    database_url: str = "sqlite:///./tripmate.db"
    
    # ChromaDB
    chroma_persist_dir: str = "./data/chroma_db"
    
    # External APIs
    openweather_api_key: str = ""
    google_places_api_key: str = ""
    
    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
