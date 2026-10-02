import streamlit as st
import httpx
import asyncio

st.set_page_config(page_title="My Trips", page_icon="📋")

st.title("📋 My Saved Trips")

async def fetch_trips():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/trips/")
            if response.status_code == 200:
                return response.json()
            else:
                st.error("Failed to fetch trips")
                return []
        except Exception as e:
            st.error("Cannot connect to backend")
            return []

with st.spinner("Loading your trips..."):
    trips = asyncio.run(fetch_trips())

if not trips:
    st.info("No trips found. Go to 'Plan Trip' to create one!")
else:
    for idx, trip in enumerate(reversed(trips)):
        with st.expander(f"📍 {trip['destination']} - {trip['num_days']} Days"):
            st.write(f"**Total Cost:** ₹{trip['total_estimated_cost']}")
            st.write(f"**Budget Status:** {trip['budget_status']}")
            
            st.subheader("Itinerary")
            for day in trip['itinerary']:
                st.markdown(f"**Day {day['day']}: {day['title']}**")
                st.markdown(f"- Activities: {', '.join(day['activities'])}")
