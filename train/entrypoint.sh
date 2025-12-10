#!/bin/bash
set -e

# Define model paths using environment variable with fallback
OUTPUT_DIR="${MODEL_OUTPUT_DIR:-/app/../models}"
MODEL_FILE="$OUTPUT_DIR/celiac_risk_model.pkl"
METADATA_FILE="$OUTPUT_DIR/model_metadata.pkl"

echo "Checking for existing model files..."

if [ "$FORCE_TRAIN" = "true" ]; then
    echo "FORCE_TRAIN is set to true. Starting training..."
    python train_model.py
elif [ -f "$MODEL_FILE" ] && [ -f "$METADATA_FILE" ]; then
    echo "Model files already exist at $MODEL_FILE and $METADATA_FILE."
    echo "Skipping training. Set FORCE_TRAIN=true to override."
    exit 0
else
    echo "Model files missing. Starting training..."
    python train_model.py
fi
