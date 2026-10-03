import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.schemas.trip import TripRequest, TripResponse, DayPlan
from src.db.engine import get_db
from src.db.models import Trip
from src.config import settings
from src.agents.graph import build_trip_graph

router = APIRouter(prefix="/api/trips", tags=["trips"])

# Compile graph once
graph = build_trip_graph()

@router.post("/plan", response_model=TripResponse)
async def plan_trip(request: TripRequest, db: Session = Depends(get_db)):
    if not settings.google_api_key or settings.google_api_key == "your-google-api-key-here":
        raise HTTPException(status_code=500, detail="Google API Key is not configured")

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
        # Run the multi-agent graph
        final_state = await graph.ainvoke(initial_state)
        
        # Prepare the response format
        result = {
            "destination": request.destination,
            "num_days": request.num_days,
            "itinerary": final_state.get("itinerary", []),
            "total_estimated_cost": final_state.get("total_estimated_cost", 0),
            "budget_status": final_state.get("budget_status", "unknown"),
            "tips": final_state.get("tips", [])
        }
        
        # Save to database
        db_trip = Trip(
            destination=request.destination,
            num_days=request.num_days,
            budget=request.budget,
            interests=",".join(request.interests),
            num_travelers=request.num_travelers,
            travel_month=request.travel_month,
            itinerary_json=json.dumps(result)
        )
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        
        return TripResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[TripResponse])
def get_trips(db: Session = Depends(get_db)):
    trips = db.query(Trip).all()
    response_trips = []
    for t in trips:
        if t.itinerary_json:
            try:
                data = json.loads(t.itinerary_json)
                response_trips.append(TripResponse(**data))
            except json.JSONDecodeError:
                pass
    return response_trips
