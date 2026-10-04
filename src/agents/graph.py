from langgraph.graph import StateGraph, START, END
from src.agents.state import TripState
from src.agents.supervisor import supervisor_node
from src.agents.research_agent import research_node
from src.agents.itinerary_agent import itinerary_node
from src.agents.budget_agent import budget_node

def build_trip_graph(checkpointer=None):
    """Build and compile the multi-agent LangGraph."""
    graph = StateGraph(TripState)
    
    # Add nodes (names must not match state keys)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research_agent", research_node)
    graph.add_node("itinerary_agent", itinerary_node)
    graph.add_node("budget_agent", budget_node)
    
    # Entry point
    graph.add_edge(START, "supervisor")
    
    # Supervisor routes to agents
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["next_agent"],
        {
            "research": "research_agent",
            "itinerary": "itinerary_agent",
            "budget": "budget_agent",
            "FINISH": END,
        }
    )
    
    # All agents route back to supervisor
    graph.add_edge("research_agent", "supervisor")
    graph.add_edge("itinerary_agent", "supervisor")
    graph.add_edge("budget_agent", "supervisor")
    
    return graph.compile(checkpointer=checkpointer)
