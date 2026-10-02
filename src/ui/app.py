import streamlit as st

st.set_page_config(
    page_title="TripMate",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🗺️ Welcome to TripMate")

st.markdown("""
### Your AI-Powered Trip Planning Assistant

TripMate helps you plan personalized, budget-aware itineraries for your next adventure.

**How to get started:**
1. Go to the **Plan Trip** page in the sidebar.
2. Enter your destination, budget, travel dates, and interests.
3. Let the AI generate a complete day-by-day itinerary for you.

*Note: Make sure your API keys are configured in the `.env` file!*
""")
