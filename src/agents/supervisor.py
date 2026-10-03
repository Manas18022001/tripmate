from src.agents.state import TripState
from langchain_core.messages import HumanMessage

def supervisor_node(state: TripState) -> dict:
    """Orchestrator that decides which agent to invoke next."""
    
    # 1. Start with Research
    if not state.get("destination_info"):
        return {"next_agent": "research"}
        
    # 2. Generate Itinerary
    if not state.get("itinerary"):
        return {"next_agent": "itinerary"}
        
    # 3. Check Budget
    if not state.get("budget_breakdown"):
        return {"next_agent": "budget"}
        
    # 4. Handle loops (if over budget, re-plan)
    if state.get("budget_status") == "over_budget":
        # Hard limit to prevent infinite loops (e.g. impossible budget)
        if state.get("iteration_count", 0) >= 3:
            return {"next_agent": "FINISH"}
        return {"next_agent": "itinerary"}
        
    # 5. Finish
    if state.get("budget_status") == "within_budget":
        return {"next_agent": "FINISH"}
        
    return {"next_agent": "FINISH"}
