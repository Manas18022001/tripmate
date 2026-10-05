import streamlit as st
import httpx
import asyncio

st.set_page_config(page_title="My Trips", page_icon="📋")

st.title("📋 My Saved Trips")

API_BASE = "http://127.0.0.1:8000"


async def fetch_trips():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/api/trips/")
            if response.status_code == 200:
                return response.json()
            else:
                st.error("Failed to fetch trips")
                return []
        except Exception:
            st.error("Cannot connect to backend. Make sure the FastAPI server is running.")
            return []


async def delete_trip(trip_id):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{API_BASE}/api/trips/{trip_id}")
            return response.status_code == 200
        except Exception:
            return False


# Fetch trips
with st.spinner("Loading your trips..."):
    trips = asyncio.run(fetch_trips())

if not trips:
    st.info("No trips found yet. Go to **Plan Trip** to create one!")
else:
    st.write(f"You have **{len(trips)}** saved trip(s).")

    for trip in trips:
        trip_id = trip.get("id", "?")
        created = trip.get("created_at", "")
        if created:
            # Show just the date part
            created = created.split("T")[0] if "T" in created else created.split(" ")[0]

        header = f"📍 {trip['destination']} — {trip['num_days']} Days"
        if created:
            header += f" (Created: {created})"

        with st.expander(header):
            col1, col2, col3 = st.columns(3)
            col1.metric("Estimated Cost", f"₹{trip['total_estimated_cost']}")
            col2.metric("Budget Status", trip['budget_status'].replace("_", " ").title())

            if trip.get("budget_breakdown"):
                diff = trip["budget_breakdown"].get("difference", 0)
                col3.metric("Budget Remaining", f"₹{diff:.0f}")

            st.subheader("Itinerary")
            for day in trip['itinerary']:
                st.markdown(f"**Day {day['day']}: {day['title']}**")
                st.markdown(f"- 🎯 Activities: {', '.join(day['activities'])}")
                st.markdown(f"- 🍽️ Meals: {', '.join(day['meals'])}")
                st.markdown(f"- 💰 Cost: ₹{day['estimated_cost']}")
                if day.get("travel_tips"):
                    st.caption(f"💡 {day['travel_tips']}")
                st.markdown("---")

            if trip.get("tips"):
                st.subheader("Tips")
                for tip in trip["tips"]:
                    st.markdown(f"- {tip}")

            # Delete button
            if st.button("🗑️ Delete Trip", key=f"del_{trip_id}"):
                success = asyncio.run(delete_trip(trip_id))
                if success:
                    st.success("Trip deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete trip.")
