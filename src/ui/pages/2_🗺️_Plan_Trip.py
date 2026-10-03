import streamlit as st
import httpx
import asyncio

st.set_page_config(page_title="Plan Trip", page_icon="🗺️")

st.title("🗺️ Plan a New Trip")

with st.form("trip_form"):
    destination = st.text_input("Destination", placeholder="e.g., Manali, Goa, Jaipur")
    
    col1, col2 = st.columns(2)
    with col1:
        num_days = st.number_input("Number of Days", min_value=1, max_value=30, value=3)
        budget = st.number_input("Total Budget (₹)", min_value=1000, value=15000, step=1000)
    
    with col2:
        num_travelers = st.number_input("Number of Travelers", min_value=1, value=2)
        travel_month = st.selectbox("Travel Month", [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
    
    interests = st.multiselect(
        "Interests",
        ["Sightseeing", "Adventure", "Food", "Culture", "Relaxation", "Nature", "Shopping"],
        default=["Sightseeing", "Food"]
    )
    
    submit_button = st.form_submit_button("Generate Itinerary ✨")

async def generate_trip(payload):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://127.0.0.1:8000/api/trips/plan", json=payload, timeout=120.0)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection error: Make sure the FastAPI backend is running! ({e})")
            return None

if submit_button:
    if not destination:
        st.warning("Please enter a destination.")
    else:
        payload = {
            "destination": destination,
            "num_days": num_days,
            "budget": budget,
            "interests": interests,
            "num_travelers": num_travelers,
            "travel_month": travel_month
        }
        
        with st.spinner(f"Planning your perfect trip to {destination}... This may take a moment."):
            result = asyncio.run(generate_trip(payload))
            
            if result:
                st.success("Trip generated successfully!")
                
                st.header(f"Trip to {result['destination']}")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Duration", f"{result['num_days']} Days")
                col2.metric("Estimated Cost", f"₹{result['total_estimated_cost']}")
                col3.metric("Budget Status", result['budget_status'])
                
                st.subheader("Day-by-Day Itinerary")
                for day in result['itinerary']:
                    with st.expander(f"Day {day['day']}: {day['title']}", expanded=True):
                        st.markdown(f"**Activities:** {', '.join(day['activities'])}")
                        st.markdown(f"**Meals:** {', '.join(day['meals'])}")
                        st.markdown(f"**Estimated Cost:** ₹{day['estimated_cost']}")
                        if day.get('travel_tips'):
                            st.info(f"💡 Tip: {day['travel_tips']}")
                
                if result.get('tips'):
                    st.subheader("General Tips")
                    for tip in result['tips']:
                        st.markdown(f"- {tip}")
