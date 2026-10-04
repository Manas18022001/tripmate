import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langgraph.checkpoint.memory import MemorySaver

from src.api.schemas.trip import TripRequest, TripResponse, BudgetBreakdown, ChatRequest, ChatResponse
from src.db.engine import get_db
from src.db.models import Trip
from src.config import settings
from src.agents.graph import build_trip_graph

router = APIRouter(prefix="/api/trips", tags=["trips"])

# Persistent checkpointer for conversation memory
checkpointer = MemorySaver()

# Compile graph with checkpointing enabled
graph = build_trip_graph(checkpointer=checkpointer)


@router.post("/plan", response_model=TripResponse)
async def plan_trip(request: TripRequest, db: Session = Depends(get_db)):

    # Generate a unique thread_id for this trip conversation
    thread_id = str(uuid.uuid4())

    initial_state = {
        "messages": [],
        "destination": request.destination,
        "num_days": request.num_days,
        "budget": request.budget,
        "interests": request.interests,
        "num_travelers": request.num_travelers,
        "travel_month": request.travel_month,
        "iteration_count": 0,
        "itinerary": [],
        "budget_breakdown": None,
    }

    try:
        # Run the multi-agent graph with checkpointing
        config = {"configurable": {"thread_id": thread_id}}
        final_state = await graph.ainvoke(initial_state, config=config)

        # Build budget breakdown
        breakdown_data = final_state.get("budget_breakdown") or {}
        breakdown = {
            "total_cost": final_state.get("total_estimated_cost", 0),
            "budget": request.budget,
            "difference": request.budget - final_state.get("total_estimated_cost", 0),
        }

        # Prepare the response
        result = {
            "destination": request.destination,
            "num_days": request.num_days,
            "itinerary": final_state.get("itinerary", []),
            "total_estimated_cost": final_state.get("total_estimated_cost", 0),
            "budget_status": final_state.get("budget_status", "unknown"),
            "budget_breakdown": breakdown,
            "tips": final_state.get("tips", []),
            "thread_id": thread_id,
        }

        # Save to database
        db_trip = Trip(
            destination=request.destination,
            num_days=request.num_days,
            budget=request.budget,
            interests=",".join(request.interests),
            num_travelers=request.num_travelers,
            travel_month=request.travel_month,
            itinerary_json=json.dumps(result),
            thread_id=thread_id,
        )
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)

        result["id"] = db_trip.id
        result["created_at"] = str(db_trip.created_at) if db_trip.created_at else None

        return TripResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[TripResponse])
def get_trips(db: Session = Depends(get_db)):
    trips = db.query(Trip).order_by(Trip.id.desc()).all()
    response_trips = []
    for t in trips:
        if t.itinerary_json:
            try:
                data = json.loads(t.itinerary_json)
                data["id"] = t.id
                data["created_at"] = str(t.created_at) if t.created_at else None
                response_trips.append(TripResponse(**data))
            except (json.JSONDecodeError, Exception):
                pass
    return response_trips


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    try:
        data = json.loads(trip.itinerary_json)
        data["id"] = trip.id
        data["created_at"] = str(trip.created_at) if trip.created_at else None
        return TripResponse(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Corrupted trip data")


@router.delete("/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return {"detail": "Trip deleted"}


@router.post("/{trip_id}/chat", response_model=ChatResponse)
async def chat_refine_trip(trip_id: int, chat_req: ChatRequest, db: Session = Depends(get_db)):
    """Refine an existing trip through conversational chat."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if not trip.thread_id:
        raise HTTPException(status_code=400, detail="This trip does not support chat refinement (no thread_id)")

    try:
        # Load the existing trip data for context
        existing_data = json.loads(trip.itinerary_json)
        existing_itinerary = json.dumps(existing_data.get("itinerary", []), indent=2)

        # Build refinement state — we re-invoke the graph with the user's message
        from langchain_core.messages import HumanMessage
        from langchain_community.chat_models import ChatOllama
        from langchain_core.output_parsers import JsonOutputParser

        llm = ChatOllama(
            model=settings.llm_model,
            temperature=0.7,
            format="json",
        )

        refinement_prompt = f"""You are TripMate, an AI trip planner. The user has an existing trip and wants to modify it.

Current Trip to {trip.destination} ({trip.num_days} days, Budget: ₹{trip.budget}, {trip.num_travelers} travelers):
{existing_itinerary}

The user says: "{chat_req.message}"

If the user wants to change the itinerary, return a JSON object with this structure:
{{
  "reply": "A friendly explanation of what you changed",
  "itinerary": [the full updated itinerary array with day, title, activities, meals, estimated_cost, travel_tips],
  "tips": ["updated tips"]
}}

If the user is just asking a question (not modifying the trip), return:
{{
  "reply": "Your helpful answer here",
  "itinerary": null,
  "tips": null
}}
"""
        chain = llm | JsonOutputParser()
        response = chain.invoke([HumanMessage(content=refinement_prompt)])

        reply = response.get("reply", "I couldn't process your request.")
        updated_trip_response = None

        # If the LLM returned an updated itinerary, save it
        if response.get("itinerary"):
            new_itinerary = response["itinerary"]
            new_tips = response.get("tips") or existing_data.get("tips", [])
            new_total_cost = sum(day.get("estimated_cost", 0) for day in new_itinerary)
            new_status = "within_budget" if new_total_cost <= trip.budget else "over_budget"

            updated_result = {
                "destination": trip.destination,
                "num_days": trip.num_days,
                "itinerary": new_itinerary,
                "total_estimated_cost": new_total_cost,
                "budget_status": new_status,
                "budget_breakdown": {
                    "total_cost": new_total_cost,
                    "budget": trip.budget,
                    "difference": trip.budget - new_total_cost,
                },
                "tips": new_tips,
                "thread_id": trip.thread_id,
            }

            # Persist updated trip
            trip.itinerary_json = json.dumps(updated_result)
            db.commit()
            db.refresh(trip)

            updated_result["id"] = trip.id
            updated_result["created_at"] = str(trip.created_at) if trip.created_at else None
            updated_trip_response = TripResponse(**updated_result)

        return ChatResponse(reply=reply, updated_trip=updated_trip_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
