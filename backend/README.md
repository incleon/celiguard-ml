# Backend Service

FastAPI REST API for the CeliGuard ML application.

## Features

- RESTful API endpoints for risk prediction
- Automatic model loading on startup
- CORS enabled for frontend communication
- Health check endpoint
- Interactive API documentation (Swagger UI)

## Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /predict` - Predict malignancy risk
- `GET /model-info` - Model information

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Running with Docker

```bash
# Build the image
docker build -t celiguard-backend .

# Run the container
docker run -p 8000:8000 -v ../models:/app/../models celiguard-backend
```

## Environment Variables

- `MODEL_PATH`: Path to trained model file (default: `../models/celiac_risk_model.pkl`)
- `METADATA_PATH`: Path to model metadata file (default: `../models/model_metadata.pkl`)

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
