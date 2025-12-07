#!/bin/bash

# Generate model if it doesn't exist
if [ ! -f "celiac_risk_model.pkl" ]; then
    echo "Training model..."
    python data_and_model.py
    echo "Model training complete!"
fi

# Start FastAPI
echo "Starting FastAPI server..."
uvicorn api:app --host 0.0.0.0 --port $PORT