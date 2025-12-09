# Training Service

Model training script for the CeliGuard ML application.

## Features

- Generates synthetic patient data (1,500 samples)
- Trains multiple ML models (Logistic Regression, Random Forest)
- Evaluates model performance
- Saves the best model and metadata
- Feature importance analysis

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Train the model
python train_model.py
```

The trained models will be saved to the `../models` directory.

## Running with Docker

```bash
# Build the image
docker build -t celiguard-train .

# Run the container
docker run -v ../models:/app/../models celiguard-train
```

## Environment Variables

- `MODEL_OUTPUT_DIR`: Directory to save trained models (default: `../models`)

## Output

The script generates:
- `celiac_risk_model.pkl` - Trained Random Forest model
- `model_metadata.pkl` - Model metadata and feature information

## Model Details

- **Algorithm**: Random Forest Classifier
- **Training Samples**: 1,500 synthetic patient records
- **Features**: 13 clinical and demographic features
  - 5 numeric features (age, BMI, years, etc.)
  - 8 categorical features (sex, Marsh grade, RCD type, etc.)
- **Output Classes**: Low Risk (0), Moderate Risk (1), High Risk (2)
- **Preprocessing**: StandardScaler + OneHotEncoder

## Performance

The model typically achieves:
- Accuracy: ~85-90% on test set
- Balanced performance across all risk classes
