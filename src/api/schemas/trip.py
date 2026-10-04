from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TripRequest(BaseModel):
    destination: str = Field(..., example="Manali")
    num_days: int = Field(..., ge=1, le=30, example=5)
    budget: float = Field(..., gt=0, example=25000)
    interests: list[str] = Field(default=["sightseeing"], example=["adventure", "food"])
    num_travelers: int = Field(default=1, ge=1, example=2)
    travel_month: str = Field(..., example="October")

class DayPlan(BaseModel):
    day: int
    title: str
    activities: list[str]
    meals: list[str]
    estimated_cost: float
    travel_tips: str = ""

class BudgetBreakdown(BaseModel):
    total_cost: float = 0
    budget: float = 0
    difference: float = 0  # positive = under budget

class TripResponse(BaseModel):
    id: Optional[int] = None
    destination: str
    num_days: int
    itinerary: list[DayPlan]
    total_estimated_cost: float
    budget_status: str
    budget_breakdown: Optional[BudgetBreakdown] = None
    tips: list[str]
    thread_id: Optional[str] = None
    created_at: Optional[datetime] = None

# --- Chat schemas ---

class ChatRequest(BaseModel):
    message: str = Field(..., example="Can you make day 2 more adventurous?")

class ChatResponse(BaseModel):
    reply: str
    updated_trip: Optional[TripResponse] = None
