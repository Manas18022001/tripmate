from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOllama
from src.agents.state import TripState
from src.agents.tools.search import search_destination_knowledge
from src.agents.tools.weather import get_weather_info
from src.config import settings

def research_node(state: TripState) -> dict:
    """Agent responsible for gathering factual information about the destination."""
    
    llm = ChatOllama(
        model=settings.llm_model,
        temperature=0.3, # Low temperature for factual research
    )
    
    system_prompt = """You are the Research Agent for TripMate.
Your job is to gather accurate, up-to-date information about the user's destination.
ALWAYS use the `search_destination_knowledge` tool first to find specific facts, prices, and seasonal advice from our database.
Extract:
1. The best areas to stay for someone with their interests.
2. Typical costs (food, local transport) to help the budget agent later.
3. Relevant seasonal or weather advice for their travel month.
Summarize your findings clearly."""

    human_msg = f"Research {state['destination']} for a {state['num_days']} day trip in {state['travel_month']}. Interests: {', '.join(state['interests'])}."
    
    # We invoke the LLM. If it decides to call tools, we'll need to execute them.
    # For a robust implementation, we would use a prebuilt react_agent or create a tool-calling loop here.
    # For simplicity in this node, we will force a tool call if we were using a structured loop,
    # but let's use LangGraph's prebuilt create_react_agent logic or manually execute the tool.
    
    # Let's manually invoke the search tool directly to ensure we get data, 
    # then feed it to the LLM to summarize. This guarantees RAG is used.
    
    raw_knowledge = search_destination_knowledge.invoke(
        {"query": f"Cost, areas to stay, and weather in {state['travel_month']}", "destination": state['destination']}
    )
    
    summary_prompt = f"""{system_prompt}
    
Here is the raw data retrieved from our database:
{raw_knowledge}

User Request: {human_msg}
Please summarize the findings."""
    
    response = llm.invoke([HumanMessage(content=summary_prompt)])
    
    return {
        "destination_info": response.content,
        "messages": [HumanMessage(content="Research completed.", name="research_agent")]
    }
