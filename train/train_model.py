"""
Celiac Disease Malignancy Risk Stratifier - Data Generation and Model Training
===============================================================================
This module generates synthetic patient data and trains ML models to predict
malignancy risk in Celiac Disease patients.

WARNING: This is a proof-of-concept with synthetic data using medically-inspired
heuristics. NOT for clinical use.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

# Set random seed for reproducibility
np.random.seed(42)

print("=" * 80)
print("CELIAC DISEASE MALIGNANCY RISK STRATIFIER - MODEL TRAINING")
print("=" * 80)


# STEP 1: GENERATE SYNTHETIC DATA
print("\n[1] Generating synthetic patient data...")

n_samples = 1500

# Generate numeric features
age_at_diagnosis = np.random.uniform(5, 80, n_samples)
current_age = age_at_diagnosis + np.random.uniform(0, 10, n_samples)
current_age = np.minimum(current_age, 90)  # Cap at 90
years_of_symptoms_before_diagnosis = np.random.uniform(0, 15, n_samples)
bmi = np.random.normal(24, 4, n_samples)
bmi = np.clip(bmi, 16, 35)
followup_years = np.minimum(current_age - age_at_diagnosis, 20)

# Generate categorical features with realistic distributions
sex = np.random.choice(['Male', 'Female'], n_samples, p=[0.4, 0.6])

# Marsh grade (3c is most severe)
marsh_grade = np.random.choice(['0', '1', '2', '3a', '3b', '3c'], n_samples,
                                p=[0.05, 0.1, 0.15, 0.2, 0.25, 0.25])

mucosal_healing = np.random.choice(['Yes', 'No'], n_samples, p=[0.65, 0.35])

# RCD Type II is rare but serious
rcd_type = np.random.choice(['None', 'RCD_I', 'RCD_II'], n_samples,
                             p=[0.85, 0.10, 0.05])

smoking_status = np.random.choice(['Never', 'Former', 'Current'], n_samples,
                                   p=[0.6, 0.25, 0.15])

gfd_adherence = np.random.choice(['Poor', 'Partial', 'Good', 'Excellent'], n_samples,
                                  p=[0.15, 0.25, 0.35, 0.25])

family_history = np.random.choice(['Yes', 'No'], n_samples, p=[0.2, 0.8])

hla_risk = np.random.choice(['Low', 'Medium', 'High'], n_samples,
                             p=[0.3, 0.5, 0.2])

# Create DataFrame
data = pd.DataFrame({
    'age_at_diagnosis': age_at_diagnosis,
    'current_age': current_age,
    'years_of_symptoms_before_diagnosis': years_of_symptoms_before_diagnosis,
    'bmi': bmi,
    'followup_years': followup_years,
    'sex': sex,
    'marsh_grade_at_diagnosis': marsh_grade,
    'mucosal_healing_on_followup': mucosal_healing,
    'rcd_type': rcd_type,
    'smoking_status': smoking_status,
    'gfd_adherence': gfd_adherence,
    'family_history_of_malignancy': family_history,
    'hla_risk': hla_risk
})


# STEP 2: CREATE TARGET LABELS USING RULE-BASED LOGIC
print("[2] Creating malignancy risk labels using clinical heuristics...")

def assign_risk_label(row):
    """
    Assign malignancy risk based on medically-inspired heuristics.
    
    HIGH RISK factors:
    - RCD Type II (very high risk)
    - Late diagnosis (>50) + no mucosal healing + poor adherence
    - Long diagnostic delay (>8 years) + severe Marsh + poor adherence
    
    LOW RISK factors:
    - Young diagnosis (<40)
    - Mucosal healing achieved
    - No RCD
    - Good/Excellent adherence
    
    MODERATE RISK: intermediate cases with some risk factors
    """
    
    # HIGH RISK CONDITIONS
    if row['rcd_type'] == 'RCD_II':
        return 2
    
    if (row['age_at_diagnosis'] > 50 and 
        row['mucosal_healing_on_followup'] == 'No' and 
        row['gfd_adherence'] in ['Poor', 'Partial']):
        return 2
    
    if (row['years_of_symptoms_before_diagnosis'] > 8 and 
        row['marsh_grade_at_diagnosis'] in ['3b', '3c'] and 
        row['gfd_adherence'] == 'Poor'):
        return 2
    
    # Additional high risk: old age + RCD_I + no healing
    if (row['age_at_diagnosis'] > 60 and 
        row['rcd_type'] == 'RCD_I' and 
        row['mucosal_healing_on_followup'] == 'No'):
        return 2
    
    # LOW RISK CONDITIONS
    if (row['age_at_diagnosis'] < 40 and 
        row['mucosal_healing_on_followup'] == 'Yes' and 
        row['rcd_type'] == 'None' and 
        row['gfd_adherence'] in ['Good', 'Excellent']):
        return 0
    
    if (row['mucosal_healing_on_followup'] == 'Yes' and 
        row['rcd_type'] == 'None' and 
        row['gfd_adherence'] == 'Excellent' and 
        row['years_of_symptoms_before_diagnosis'] < 3):
        return 0
    
    # MODERATE RISK: everything else with some stochasticity
    # Add slight randomness to avoid hard boundaries
    if np.random.random() < 0.15:
        # 15% chance to shift between moderate and neighbors
        return np.random.choice([0, 1, 2], p=[0.3, 0.4, 0.3])
    
    return 1  # Default moderate risk

data['malignancy_risk'] = data.apply(assign_risk_label, axis=1)

print(f"Generated {len(data)} patient records")
print("\nLabel distribution:")
print(data['malignancy_risk'].value_counts().sort_index())
print("\nLabel percentages:")
print(data['malignancy_risk'].value_counts(normalize=True).sort_index() * 100)


# STEP 3: PREPARE DATA FOR TRAINING
print("\n[3] Preparing data for model training...")

# Define feature columns
numeric_features = [
    'age_at_diagnosis', 'current_age', 'years_of_symptoms_before_diagnosis',
    'bmi', 'followup_years'
]

categorical_features = [
    'sex', 'marsh_grade_at_diagnosis', 'mucosal_healing_on_followup',
    'rcd_type', 'smoking_status', 'gfd_adherence',
    'family_history_of_malignancy', 'hla_risk'
]

X = data[numeric_features + categorical_features]
y = data['malignancy_risk']

# Split data with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")


# STEP 4: CREATE PREPROCESSING PIPELINE
print("\n[4] Creating preprocessing pipeline...")

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ]
)


# STEP 5: TRAIN AND EVALUATE MODELS
print("\n[5] Training models...\n")

# Model 1: Logistic Regression (baseline)
print("-" * 80)
print("MODEL 1: Logistic Regression (Baseline)")
print("-" * 80)

lr_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000, random_state=42))
])

lr_pipeline.fit(X_train, y_train)
y_pred_lr = lr_pipeline.predict(X_test)

print(f"\nAccuracy: {accuracy_score(y_test, y_pred_lr):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_lr, 
                          target_names=['Low Risk', 'Moderate Risk', 'High Risk']))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_lr))

# Model 2: Random Forest (main model)
print("\n" + "-" * 80)
print("MODEL 2: Random Forest Classifier")
print("-" * 80)

rf_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=200, max_depth=10,
                                         random_state=42, n_jobs=-1))
])

rf_pipeline.fit(X_train, y_train)
y_pred_rf = rf_pipeline.predict(X_test)

print(f"\nAccuracy: {accuracy_score(y_test, y_pred_rf):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_rf,
                          target_names=['Low Risk', 'Moderate Risk', 'High Risk']))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_rf))


# STEP 6: SELECT BEST MODEL AND SHOW FEATURE IMPORTANCES
print("\n" + "=" * 80)
print("MODEL SELECTION")
print("=" * 80)

lr_accuracy = accuracy_score(y_test, y_pred_lr)
rf_accuracy = accuracy_score(y_test, y_pred_rf)

print(f"\nLogistic Regression Accuracy: {lr_accuracy:.4f}")
print(f"Random Forest Accuracy: {rf_accuracy:.4f}")

if rf_accuracy >= lr_accuracy:
    final_model = rf_pipeline
    model_name = "Random Forest"
    print(f"\n✓ Selected: {model_name} (better performance)")
else:
    final_model = lr_pipeline
    model_name = "Logistic Regression"
    print(f"\n✓ Selected: {model_name} (better performance)")

# Feature importances for Random Forest
if model_name == "Random Forest":
    print("\n" + "-" * 80)
    print("FEATURE IMPORTANCES (Random Forest)")
    print("-" * 80)
    
    # Get feature names after preprocessing
    feature_names = (numeric_features + 
                    list(rf_pipeline.named_steps['preprocessor']
                         .named_transformers_['cat']
                         .get_feature_names_out(categorical_features)))
    
    importances = rf_pipeline.named_steps['classifier'].feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance_df.head(10).to_string(index=False))


# STEP 7: SAVE THE MODEL
print("\n" + "=" * 80)
print("SAVING MODEL")
print("=" * 80)

# Create output directory if it doesn't exist
output_dir = os.getenv('MODEL_OUTPUT_DIR', '../models')
os.makedirs(output_dir, exist_ok=True)

model_filename = os.path.join(output_dir, 'celiac_risk_model.pkl')
metadata_filename = os.path.join(output_dir, 'model_metadata.pkl')

joblib.dump(final_model, model_filename)
print(f"\n✓ Model saved to: {model_filename}")

# Also save the feature names for reference
metadata = {
    'numeric_features': numeric_features,
    'categorical_features': categorical_features,
    'model_type': model_name,
    'accuracy': rf_accuracy if model_name == "Random Forest" else lr_accuracy
}
joblib.dump(metadata, metadata_filename)
print(f"✓ Metadata saved to: {metadata_filename}")

print("\n" + "=" * 80)
print("TRAINING COMPLETE!")
print("=" * 80)
print(f"\nFinal model: {model_name}")
print(f"Test accuracy: {metadata['accuracy']:.4f}")
print("\nThe model is ready for deployment via FastAPI.")
