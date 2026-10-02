from sqlalchemy import Column, Integer, String, Float, Text
from src.db.engine import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, index=True)
    num_days = Column(Integer)
    budget = Column(Float)
    interests = Column(String)  # Stored as comma-separated string
    num_travelers = Column(Integer)
    travel_month = Column(String)
    itinerary_json = Column(Text, nullable=True)  # Store JSON response string
