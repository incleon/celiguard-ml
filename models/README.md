# Models Directory

This directory contains the trained machine learning models.

## Files

- `celiac_risk_model.pkl` - Trained Random Forest model
- `model_metadata.pkl` - Model metadata and feature information

## Generation

Models are automatically generated when running the training service:

```bash
# Using Docker
docker-compose up train

# Or manually
cd train
python train_model.py
```

The models will be saved to this directory and shared with the backend service via Docker volumes.
