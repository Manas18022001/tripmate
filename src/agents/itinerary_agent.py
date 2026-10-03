import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from src.agents.state import TripState
from src.config import settings

def itinerary_node(state: TripState) -> dict:
    """Agent responsible for generating the day-by-day itinerary."""
    
    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=0.7,
    )
    
    # If the budget agent flagged this as over budget, we add a constraint to the prompt
    budget_constraint = ""
    if state.get("budget_status") == "over_budget":
        budget_constraint = f"WARNING: Your previous itinerary was OVER BUDGET. You must suggest cheaper activities and meals to fit within ₹{state['budget']} total."

    system_prompt = f"""You are the Itinerary Agent for TripMate.
Based on the research provided, create a personalized {state['num_days']}-day itinerary for {state['destination']}.
The user's budget is ₹{state['budget']}.
Their interests are: {', '.join(state['interests'])}.
{budget_constraint}

You must return ONLY a JSON object with this exact structure:
{{
  "itinerary": [
    {{
      "day": 1,
      "title": "Arrival and local exploration",
      "activities": ["Activity 1", "Activity 2"],
      "meals": ["Lunch at Cafe X", "Dinner at Y"],
      "estimated_cost": 1500,
      "travel_tips": "Tip here"
    }}
  ],
  "tips": ["General tip 1", "General tip 2"]
}}
"""

    human_msg = f"Research Data:\n{state.get('destination_info', 'No research available.')}"
    
    chain = llm | JsonOutputParser()
    
    response = chain.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_msg)
    ])
    
    total_cost = sum(day.get("estimated_cost", 0) for day in response.get("itinerary", []))
    
    return {
        "itinerary": response.get("itinerary", []),
        "tips": response.get("tips", []),
        "total_estimated_cost": total_cost,
        "messages": [HumanMessage(content="Itinerary generated.", name="itinerary_agent")]
    }
