# 🚀 Quick Start Guide

Get CeliGuard ML up and running in minutes!

## Prerequisites

- Docker and Docker Compose installed
- Ports 8000 and 8501 available

## Option 1: Docker (Recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/celiguard-ml.git
cd celiguard-ml
```

### Step 2: Start All Services
```bash
docker-compose up --build
```

Wait for the services to start. You'll see:
- ✓ Model training complete
- ✓ Backend API running on port 8000
- ✓ Frontend running on port 8501

### Step 3: Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

### Step 4: Make a Prediction

1. Fill in the patient information in the web form
2. Click "Predict Risk"
3. View the risk assessment and recommendations

### Stop the Application
```bash
docker-compose down
```

## Advanced Configuration

### Force Retraining
By default, the training service skips if a model exists. To force retraining:

```bash
FORCE_TRAIN=true docker-compose up -d --build train
```

### Configure Dataset Size
To train on a larger dataset (e.g., 10,000 samples):

```bash
N_SAMPLES=10000 docker-compose up -d --build train
```

## Option 2: Using Makefile

If you have `make` installed:

```bash
# Build all services
make build

# Start all services
make up

# View logs
make logs

# Stop all services
make down
```

## Option 3: Manual Setup (Development)

### Train the Model
```bash
cd train
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
cd ..
```

### Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

### Start Frontend (New Terminal)
```bash
cd frontend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Testing the API

### Using curl
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age_at_diagnosis": 45,
    "current_age": 50,
    "years_of_symptoms_before_diagnosis": 5,
    "bmi": 24.5,
    "followup_years": 5,
    "sex": "Female",
    "marsh_grade_at_diagnosis": "3b",
    "mucosal_healing_on_followup": "Yes",
    "rcd_type": "None",
    "smoking_status": "Never",
    "gfd_adherence": "Good",
    "family_history_of_malignancy": "No",
    "hla_risk": "Medium"
  }'
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "age_at_diagnosis": 45,
        "current_age": 50,
        "years_of_symptoms_before_diagnosis": 5,
        "bmi": 24.5,
        "followup_years": 5,
        "sex": "Female",
        "marsh_grade_at_diagnosis": "3b",
        "mucosal_healing_on_followup": "Yes",
        "rcd_type": "None",
        "smoking_status": "Never",
        "gfd_adherence": "Good",
        "family_history_of_malignancy": "No",
        "hla_risk": "Medium"
    }
)

print(response.json())
```

## Troubleshooting

### Port Already in Use
If ports 8000 or 8501 are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
  - "8502:8501"  # Change 8501 to 8502
```

### Model Not Found
If you see "Model not loaded" error:
1. Ensure the training service completed successfully
2. Check that `models/` directory contains `.pkl` files
3. Restart the backend service

### Cannot Connect to API
If frontend can't connect to backend:
1. Verify backend is running: http://localhost:8000/health
2. Check Docker network: `docker network ls`
3. Restart all services: `docker-compose restart`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Check individual service READMEs in `backend/`, `frontend/`, and `train/`

## Support

For issues or questions, please contact the research team.
