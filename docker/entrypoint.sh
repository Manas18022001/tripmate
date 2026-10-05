#!/bin/bash
set -e

# Start FastAPI backend in the background
echo "Starting FastAPI backend..."
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend in the foreground
echo "Starting Streamlit frontend..."
streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0
