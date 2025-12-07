#!/bin/bash

# Generate model on first deployment
if [ ! -f "celiac_risk_model.pkl" ]; then
    echo "Generating model for first time..."
    python data_and_model.py
fi

# Start FastAPI in background
echo "Starting FastAPI..."
uvicorn api:app --host 0.0.0.0 --port 8000 &

# Wait for API to start
sleep 5

# Start Streamlit on main port
echo "Starting Streamlit..."
streamlit run frontend.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
