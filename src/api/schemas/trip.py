from pydantic import BaseModel, Field

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
    travel_tips: str

class TripResponse(BaseModel):
    destination: str
    num_days: int
    itinerary: list[DayPlan]
    total_estimated_cost: float
    budget_status: str
    tips: list[str]
