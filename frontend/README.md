# Frontend Service

Streamlit web interface for the CeliGuard ML application.

## Features

- Interactive patient data input form
- Real-time risk prediction
- Color-coded risk visualization
- Clinical interpretation and recommendations
- Responsive design

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Running with Docker

```bash
# Build the image
docker build -t celiguard-frontend .

# Run the container
docker run -p 8501:8501 -e API_URL=http://backend:8000 celiguard-frontend
```

## Environment Variables

- `API_URL`: Backend API URL (default: `http://localhost:8000`)

## Usage

1. Open http://localhost:8501 in your browser
2. Fill in the patient information form
3. Click "Predict Risk" to get the malignancy risk assessment
4. Review the risk classification, probabilities, and recommendations
