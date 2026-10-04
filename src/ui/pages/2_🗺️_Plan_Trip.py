import streamlit as st
import httpx
import asyncio

st.set_page_config(page_title="Plan Trip", page_icon="🗺️")

st.title("🗺️ Plan a New Trip")

API_BASE = "http://127.0.0.1:8000"

# Initialize session state for the generated trip
if "current_trip" not in st.session_state:
    st.session_state.current_trip = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
            response = await client.post(f"{API_BASE}/api/trips/plan", json=payload, timeout=120.0)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection error: Make sure the FastAPI backend is running! ({e})")
            return None


async def send_chat(trip_id, message):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/api/trips/{trip_id}/chat",
                json={"message": message},
                timeout=120.0,
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Chat error: {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection error: {e}")
            return None


def display_trip(result):
    """Render a trip result in the UI."""
    st.header(f"📍 Trip to {result['destination']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Duration", f"{result['num_days']} Days")
    col2.metric("Estimated Cost", f"₹{result['total_estimated_cost']}")
    col3.metric("Budget Status", result['budget_status'].replace("_", " ").title())

    # Budget breakdown
    if result.get("budget_breakdown"):
        bd = result["budget_breakdown"]
        diff = bd.get("difference", 0)
        if diff >= 0:
            st.success(f"💰 You have ₹{diff:.0f} remaining in your budget.")
        else:
            st.warning(f"⚠️ You are ₹{abs(diff):.0f} over your budget.")

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


# --- Handle trip generation ---
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
            "travel_month": travel_month,
        }
        with st.spinner(f"Planning your perfect trip to {destination}... This may take a moment."):
            result = asyncio.run(generate_trip(payload))
            if result:
                st.session_state.current_trip = result
                st.session_state.chat_history = []
                st.success("Trip generated successfully!")


# --- Display the current trip ---
if st.session_state.current_trip:
    result = st.session_state.current_trip
    display_trip(result)

    # --- Chat Refinement Section ---
    st.divider()
    st.subheader("💬 Refine Your Trip")
    st.caption("Ask me to change activities, swap days, adjust the budget, or answer questions about your trip.")

    # Show chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    user_message = st.chat_input("e.g., Make day 2 more adventurous")
    if user_message and result.get("id"):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.write(user_message)

        # Send to backend
        with st.spinner("Thinking..."):
            chat_result = asyncio.run(send_chat(result["id"], user_message))

        if chat_result:
            reply = chat_result.get("reply", "Something went wrong.")
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.write(reply)

            # If the trip was updated, refresh the display
            if chat_result.get("updated_trip"):
                st.session_state.current_trip = chat_result["updated_trip"]
                st.rerun()
