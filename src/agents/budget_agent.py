from src.agents.state import TripState
from langchain_core.messages import HumanMessage

def budget_node(state: TripState) -> dict:
    """Agent responsible for evaluating if the itinerary fits the budget."""
    
    budget = state['budget']
    total_cost = state.get('total_estimated_cost', 0)
    
    # A simple deterministic rule instead of an LLM call for budget evaluation
    # to save tokens and ensure strict mathematical compliance.
    
    if total_cost > budget:
        status = "over_budget"
        msg = f"Itinerary rejected. Estimated cost (₹{total_cost}) exceeds budget (₹{budget}). Sending back to Itinerary Agent for optimization."
    else:
        status = "within_budget"
        msg = f"Itinerary approved. Estimated cost (₹{total_cost}) is within budget (₹{budget})."
        
    # We could also use an LLM here to generate a detailed breakdown, but simple logic works best for routing.
    breakdown = {
        "total_cost": total_cost,
        "budget": budget,
        "difference": budget - total_cost
    }
    
    return {
        "budget_breakdown": breakdown,
        "budget_status": status,
        "iteration_count": state.get("iteration_count", 0) + 1,
        "messages": [HumanMessage(content=msg, name="budget_agent")]
    }
