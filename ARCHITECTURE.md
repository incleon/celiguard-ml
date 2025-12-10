# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CeliGuard ML System                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │
│   Training   │      │   Backend    │      │   Frontend   │
│   Service    │──────│   (FastAPI)  │──────│  (Streamlit) │
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     │                     │
       │                     │                     │
       ▼                     ▼                     │
┌──────────────────────────────────┐              │
│       Shared Models Volume        │              │
│  - celiac_risk_model.pkl         │              │
│  - model_metadata.pkl            │              │
└──────────────────────────────────┘              │
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │   User Browser  │
                                          │  localhost:8501 │
                                          └─────────────────┘
```

## Component Details

### 1. Training Service
- **Purpose**: Generate synthetic data and train ML model
- **Technology**: Python, scikit-learn, pandas, numpy
- **Input**: None (generates synthetic data)
- **Output**: Trained model files (.pkl)
- **Runtime**: Runs once, then exits
- **Port**: None (batch job)

### 2. Backend Service (FastAPI)
- **Purpose**: REST API for risk predictions
- **Technology**: FastAPI, uvicorn, joblib
- **Input**: Patient data (JSON)
- **Output**: Risk predictions (JSON)
- **Runtime**: Continuous
- **Port**: 8000
- **Endpoints**:
  - `GET /` - API info
  - `GET /health` - Health check
  - `POST /predict` - Risk prediction
  - `GET /model-info` - Model details

### 3. Frontend Service (Streamlit)
- **Purpose**: Web UI for user interaction
- **Technology**: Streamlit, requests
- **Input**: User form data
- **Output**: Visual risk assessment
- **Runtime**: Continuous
- **Port**: 8501
- **Features**:
  - Patient data input form
  - Risk visualization
  - Clinical recommendations

## Data Flow

```
1. User Input
   └─> Frontend (Streamlit)
       └─> HTTP POST to Backend
           └─> Backend loads model
               └─> Model prediction
                   └─> JSON response
                       └─> Frontend displays results
                           └─> User sees risk assessment
```

## Docker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
│                    (celiguard-network)                       │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  train:latest  │  │backend:latest  │  │frontend:     │  │
│  │                │  │                │  │latest        │  │
│  │  Port: None    │  │  Port: 8000    │  │Port: 8501    │  │
│  └────────┬───────┘  └────────┬───────┘  └──────┬───────┘  │
│           │                   │                  │          │
│           └───────────────────┴──────────────────┘          │
│                               │                             │
│                               ▼                             │
│                    ┌──────────────────┐                     │
│                    │  models volume   │                     │
│                    │  (shared)        │                     │
│                    └──────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Host Machine    │
                    │  ./models/       │
                    └──────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.115.5
- **Server**: Uvicorn 0.34.0
- **ML**: scikit-learn 1.6.0
- **Data**: pandas 2.2.3, numpy 2.2.1
- **Serialization**: joblib 1.4.2

### Frontend
- **Framework**: Streamlit 1.40.2
- **HTTP Client**: requests 2.32.3

### Training
- **ML**: scikit-learn 1.6.0
- **Data**: pandas 2.2.3, numpy 2.2.1
- **Serialization**: joblib 1.4.2

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Base Image**: Python 3.11-slim

## Security Considerations

1. **CORS**: Currently set to allow all origins (`*`) - should be restricted in production
2. **Input Validation**: Pydantic models validate all API inputs
3. **Model Files**: Stored in shared volume, read-only access for backend
4. **Network**: Services communicate via internal Docker network
5. **Ports**: Only 8000 and 8501 exposed to host

## Scalability

### Current Architecture
- Single instance of each service
- Suitable for development and small-scale deployment

### Production Recommendations
1. **Load Balancing**: Add nginx/traefik for backend load balancing
2. **Replicas**: Scale backend service horizontally
3. **Caching**: Add Redis for prediction caching
4. **Database**: Store predictions and audit logs
5. **Monitoring**: Add Prometheus + Grafana
6. **Logging**: Centralized logging with ELK stack

## Deployment Options

### Local Development
```bash
docker-compose up
```

### Production (Example with replicas)
```yaml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Cloud Deployment
- **AWS**: ECS/Fargate or EKS
- **GCP**: Cloud Run or GKE
- **Azure**: Container Instances or AKS
- **Render**: Web Services (current deployment)

## Model Lifecycle

```
1. Development
   ├─> Generate synthetic data
   ├─> Train multiple models
   ├─> Evaluate performance
   └─> Select best model

2. Deployment
   ├─> Save model to shared volume
   ├─> Backend loads model on startup
   └─> Model ready for predictions

3. Updates
   ├─> Retrain with new data
   ├─> Save new model version
   ├─> Restart backend to load new model
   └─> Zero-downtime with blue-green deployment
```

## Monitoring & Health Checks

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Frontend Health Check
```bash
curl http://localhost:8501/_stcore/health
```

### Docker Health Checks
- Backend: HTTP check every 30s
- Frontend: HTTP check every 30s
- Automatic restart on failure
