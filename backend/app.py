"""
Celiac Disease Malignancy Risk Stratifier - FastAPI Backend
============================================================
REST API that exposes the trained ML model for malignancy risk prediction.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
from typing import List
import os

from contextlib import asynccontextmanager

# LIFESPAN MANAGER (Replaces @app.on_event("startup"))
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the trained model and metadata when the API starts.
    Clean up resources when the API shuts down.
    """
    try:
        model_path = os.getenv('MODEL_PATH', '../models/celiac_risk_model.pkl')
        metadata_path = os.getenv('METADATA_PATH', '../models/model_metadata.pkl')
        
        # Store in app.state instead of global variables
        app.state.model = joblib.load(model_path)
        app.state.metadata = joblib.load(metadata_path)
        
        print("✓ Model loaded successfully")
        print(f"  Model type: {app.state.metadata['model_type']}")
        print(f"  Accuracy: {app.state.metadata['accuracy']:.4f}")
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        # We don't raise here to allow the app to start even if model fails
        # Health check will report the failure
        app.state.model = None
        app.state.metadata = None
        
    yield
    
    # Cleanup (if needed)
    app.state.model = None

# INITIALIZE FASTAPI APP
app = FastAPI(
    title="CeliGuard ML API",
    description="Predicts malignancy risk for Celiac Disease patients",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PYDANTIC MODELS FOR REQUEST/RESPONSE
class PatientInput(BaseModel):
    """Input schema for patient data"""
    age_at_diagnosis: float = Field(..., ge=5, le=80, description="Age at Celiac diagnosis (years)")
    current_age: float = Field(..., ge=5, le=90, description="Current age (years)")
    years_of_symptoms_before_diagnosis: float = Field(..., ge=0, le=15, description="Years of symptoms before diagnosis")
    bmi: float = Field(..., ge=16, le=35, description="Body Mass Index")
    followup_years: float = Field(..., ge=0, le=20, description="Years of follow-up since diagnosis")
    sex: str = Field(..., description="Patient sex (Male/Female)")
    marsh_grade_at_diagnosis: str = Field(..., description="Marsh grade at diagnosis (0, 1, 2, 3a, 3b, 3c)")
    mucosal_healing_on_followup: str = Field(..., description="Mucosal healing status (Yes/No)")
    rcd_type: str = Field(..., description="RCD type (None, RCD_I, RCD_II)")
    smoking_status: str = Field(..., description="Smoking status (Never, Former, Current)")
    gfd_adherence: str = Field(..., description="Gluten-free diet adherence (Poor, Partial, Good, Excellent)")
    family_history_of_malignancy: str = Field(..., description="Family history of malignancy (Yes/No)")
    hla_risk: str = Field(..., description="HLA risk level (Low, Medium, High)")

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class PredictionResponse(BaseModel):
    """Response schema for predictions"""
    risk_class: str
    risk_score: List[float]
    message: str


# HELPER FUNCTIONS
def generate_explanation(input_data: dict, risk_class: str) -> str:
    """
    Generate a human-readable explanation for the prediction based on
    patient characteristics and risk factors.
    """
    
    if risk_class == "High":
        reasons = []
        
        if input_data['rcd_type'] == 'RCD_II':
            reasons.append("Refractory Celiac Disease Type II (very high risk factor)")
        elif input_data['rcd_type'] == 'RCD_I':
            reasons.append("Refractory Celiac Disease Type I")
        
        if input_data['age_at_diagnosis'] > 50:
            reasons.append(f"late diagnosis at age {input_data['age_at_diagnosis']:.0f}")
        
        if input_data['mucosal_healing_on_followup'] == 'No':
            reasons.append("no mucosal healing on follow-up")
        
        if input_data['gfd_adherence'] in ['Poor', 'Partial']:
            reasons.append(f"{input_data['gfd_adherence'].lower()} adherence to gluten-free diet")
        
        if input_data['years_of_symptoms_before_diagnosis'] > 8:
            reasons.append(f"long diagnostic delay ({input_data['years_of_symptoms_before_diagnosis']:.1f} years)")
        
        if input_data['marsh_grade_at_diagnosis'] in ['3b', '3c']:
            reasons.append(f"severe intestinal damage (Marsh {input_data['marsh_grade_at_diagnosis']})")
        
        if reasons:
            return f"HIGH RISK: Key factors include {', '.join(reasons)}. Close monitoring and specialist follow-up recommended."
        else:
            return "HIGH RISK: Multiple risk factors present. Close monitoring and specialist follow-up recommended."
    
    elif risk_class == "Moderate":
        factors = []
        
        if input_data['age_at_diagnosis'] > 40:
            factors.append("diagnosis after age 40")
        
        if input_data['mucosal_healing_on_followup'] == 'No':
            factors.append("incomplete mucosal healing")
        
        if input_data['gfd_adherence'] in ['Partial']:
            factors.append("partial diet adherence")
        
        if input_data['years_of_symptoms_before_diagnosis'] > 5:
            factors.append("diagnostic delay")
        
        if factors:
            return f"MODERATE RISK: Some risk factors present including {', '.join(factors)}. Regular follow-up and monitoring advised."
        else:
            return "MODERATE RISK: Mixed risk profile. Regular follow-up and monitoring advised."
    
    else:  # Low risk
        protective = []
        
        if input_data['age_at_diagnosis'] < 40:
            protective.append("early diagnosis")
        
        if input_data['mucosal_healing_on_followup'] == 'Yes':
            protective.append("successful mucosal healing")
        
        if input_data['rcd_type'] == 'None':
            protective.append("no refractory disease")
        
        if input_data['gfd_adherence'] in ['Good', 'Excellent']:
            protective.append(f"{input_data['gfd_adherence'].lower()} diet adherence")
        
        if protective:
            return f"LOW RISK: Favorable profile with {', '.join(protective)}. Continue current management and routine follow-up."
        else:
            return "LOW RISK: Favorable risk profile. Continue current management and routine follow-up."


# API ENDPOINTS
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Celiac Disease Malignancy Risk Stratifier API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/predict": "POST - Predict malignancy risk"
        }
    }


from fastapi import Request

@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint"""
    model_loaded = getattr(request.app.state, 'model', None) is not None
    metadata = getattr(request.app.state, 'metadata', None)
    
    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "model_type": metadata['model_type'] if metadata else None
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_risk(patient: PatientInput, request: Request):
    """
    Predict malignancy risk for a Celiac Disease patient.
    """
    model = getattr(request.app.state, 'model', None)
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert input to DataFrame (model expects this format)
        input_dict = patient.dict()
        input_df = pd.DataFrame([input_dict])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        prediction_proba = model.predict_proba(input_df)[0]
        
        # Map numeric prediction to string label
        risk_mapping = {
            0: "Low",
            1: "Moderate",
            2: "High"
        }
        risk_class = risk_mapping[prediction]
        
        # Generate explanation
        explanation = generate_explanation(input_dict, risk_class)
        
        return PredictionResponse(
            risk_class=risk_class,
            risk_score=prediction_proba.tolist(),
            message=explanation
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/model-info")
async def model_info(request: Request):
    """Get information about the loaded model"""
    model = getattr(request.app.state, 'model', None)
    metadata = getattr(request.app.state, 'metadata', None)
    
    if model is None or metadata is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": metadata['model_type'],
        "accuracy": metadata['accuracy'],
        "numeric_features": metadata['numeric_features'],
        "categorical_features": metadata['categorical_features']
    }


# MAIN
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
