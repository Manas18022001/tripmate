import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from src.api.schemas.trip import TripRequest, TripResponse, DayPlan
from src.db.engine import get_db
from src.db.models import Trip
from src.config import settings

router = APIRouter(prefix="/api/trips", tags=["trips"])

@router.post("/plan", response_model=TripResponse)
async def plan_trip(request: TripRequest, db: Session = Depends(get_db)):
    if not settings.google_api_key or settings.google_api_key == "your-google-api-key-here":
        raise HTTPException(status_code=500, detail="Google API Key is not configured")

    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=settings.llm_temperature,
    )
    
    # We define the expected JSON schema clearly in the prompt to help the LLM.
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are TripMate, an expert Indian travel planner. 
You must respond ONLY with a valid JSON object matching the following structure:
{{
  "destination": "string",
  "num_days": 1,
  "itinerary": [
    {{
      "day": 1,
      "title": "string",
      "activities": ["string", "string"],
      "meals": ["string", "string"],
      "estimated_cost": 1000.0,
      "travel_tips": "string"
    }}
  ],
  "total_estimated_cost": 1000.0,
  "budget_status": "string",
  "tips": ["string", "string"]
}}
"""),
        ("human", """Plan a trip with these details:
Destination: {destination}
Days: {num_days}
Budget: ₹{budget}
Interests: {interests}
Travelers: {num_travelers}
Month: {travel_month}
"""),
    ])
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = await chain.ainvoke(request.model_dump())
        
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
    # For now, we will return empty list or just map itinerary_json
    response_trips = []
    for t in trips:
        if t.itinerary_json:
            try:
                data = json.loads(t.itinerary_json)
                response_trips.append(TripResponse(**data))
            except json.JSONDecodeError:
                pass
    return response_trips
