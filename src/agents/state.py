from typing import TypedDict, Annotated, Literal, List, Dict
from operator import add

class TripState(TypedDict):
    """Shared state across all agents in the trip planning graph."""
    
    # We don't inherit MessagesState directly because we want more strict control over our schema for now
    messages: Annotated[list, add]
    
    # User input
    destination: str
    num_days: int
    budget: float  # in INR
    interests: list[str]
    num_travelers: int
    travel_month: str
    
    # Research agent output
    destination_info: str
    weather_info: str
    
    # Itinerary agent output (we keep it as a dict to be easily serialized later)
    itinerary: List[Dict]
    total_estimated_cost: float
    tips: List[str]
    
    # Budget agent output
    budget_breakdown: Dict
    budget_status: Literal["within_budget", "over_budget", "optimized", ""]
    
    # Supervisor control
    next_agent: str
    iteration_count: int
