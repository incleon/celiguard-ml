# CeliGuard ML - Celiac Disease Malignancy Risk Stratifier

🏥 A machine learning application that predicts malignancy risk in Celiac Disease patients.

## ⚠️ Disclaimer
This is a proof-of-concept using synthetic data. NOT intended for clinical decision-making.

## 🚀 Features
- Random Forest ML model trained on synthetic patient data
- FastAPI REST API backend
- Interactive Streamlit web interface
- Color-coded risk predictions (Low/Moderate/High)
- Clinical explanations for predictions

## 🏗️ Architecture
- **ML Model:** scikit-learn Random Forest Classifier
- **Backend:** FastAPI + Uvicorn
- **Frontend:** Streamlit
- **Data:** Synthetic patient records (1500 samples)

## 📊 Input Features
13 clinical features including:
- Demographics (age, sex, BMI)
- Clinical markers (Marsh grade, RCD type)
- Lifestyle factors (diet adherence, smoking)
- Follow-up data (mucosal healing status)

## 🛠️ Local Setup

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/celiguard-ml.git
cd celiguard-ml

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate model
python data_and_model.py

# Start API (Terminal 1)
uvicorn api:app --reload

# Start Frontend (Terminal 2)
streamlit run frontend.py
```

## 🌐 Live Demo
[Add your Streamlit Cloud URL here after deployment]

## 👥 Research Team
- Aditya Tiwari
- Ayush Yadav
- Harshit Somvanshi
- Hritik Tiwari

## 📄 License
This project is for educational and research purposes.