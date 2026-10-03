import asyncio
from src.agents.graph import build_trip_graph

async def main():
    graph = build_trip_graph()
    initial_state = {
        'messages': [],
        'destination': 'Manali',
        'num_days': 3,
        'budget': 10000,
        'interests': ['Sightseeing'],
        'num_travelers': 2,
        'travel_month': 'October',
        'iteration_count': 0,
        'itinerary': [],
        'budget_breakdown': None,
    }
    print('Starting graph...')
    try:
        final_state = await graph.ainvoke(initial_state)
        print('Finished!')
        print(final_state.get('budget_status'))
    except Exception as e:
        print('Error:', str(e))

if __name__ == "__main__":
    asyncio.run(main())
