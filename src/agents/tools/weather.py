import httpx
from langchain_core.tools import tool
from src.config import settings

@tool
def get_weather_info(destination: str, month: str) -> str:
    """Get weather information for a destination in a specific month.
    Useful for recommending what to pack and which activities are suitable.
    
    Args:
        destination: The name of the destination (e.g., 'Manali', 'Goa')
        month: The month of travel (e.g., 'October')
    """
    
    # In a real app we'd use OpenWeatherMap API here.
    # For now, we will return a simulated or generic response because getting historical 
    # weather for a specific month requires a paid API plan usually.
    # We will encourage the research agent to rely on the FAISS Knowledge Base instead,
    # but this tool exists as a fallback.
    
    return f"Weather data requested for {destination} in {month}. Please cross-reference with the Knowledge Base for seasonal details."
