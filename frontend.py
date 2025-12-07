"""
Celiac Disease Malignancy Risk Stratifier - Streamlit Frontend
===============================================================
User interface for predicting malignancy risk in Celiac Disease patients.
"""

import streamlit as st
import requests
import json
import os

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Celiac Disease Risk Stratifier",
    page_icon="🏥",
    layout="wide"
)


# API CONFIGURATION
API_URL = os.getenv("API_URL", "http://localhost:8000")


# HELPER FUNCTIONS
def check_api_health():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def predict_risk(patient_data):
    """Send patient data to API and get prediction"""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=patient_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Make sure the FastAPI server is running."
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        return None, f"API error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def get_risk_color(risk_class):
    """Return color based on risk level"""
    colors = {
        "Low": "#28a745",      # Green
        "Moderate": "#fd7e14",  # Orange
        "High": "#dc3545"       # Red
    }
    return colors.get(risk_class, "#6c757d")


# MAIN APP
def main():
    # Header
    st.title("🏥 CeliGuard ML")
    st.markdown("""
    This tool predicts malignancy risk in Celiac Disease patients using machine learning.
    
    **⚠️ DISCLAIMER:** This is a proof-of-concept using synthetic data. 
    NOT intended for clinical decision-making.
    """)
    
    st.markdown("---")
    
    # Check API status
    api_status = check_api_health()
    if api_status:
        st.success("✓ Connected to prediction API")
    else:
        st.error("✗ Cannot connect to API. Please start the FastAPI server first.")
        st.info("Run: `uvicorn api:app --reload` in your terminal")
        st.stop()
    
    # Create two columns for input form
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Patient Demographics & History")
        
        age_at_diagnosis = st.number_input(
            "Age at Diagnosis (years)",
            min_value=5.0,
            max_value=80.0,
            value=45.0,
            step=1.0,
            help="Age when Celiac Disease was first diagnosed"
        )
        
        current_age = st.number_input(
            "Current Age (years)",
            min_value=age_at_diagnosis,
            max_value=90.0,
            value=max(50.0, age_at_diagnosis + 5),
            step=1.0,
            help="Patient's current age"
        )
        
        years_symptoms = st.number_input(
            "Years of Symptoms Before Diagnosis",
            min_value=0.0,
            max_value=15.0,
            value=3.0,
            step=0.5,
            help="Duration of symptoms before Celiac diagnosis (diagnostic delay)"
        )
        
        followup_years = st.number_input(
            "Years of Follow-up",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            help="Years since diagnosis on gluten-free diet"
        )
        
        bmi = st.number_input(
            "BMI (Body Mass Index)",
            min_value=16.0,
            max_value=35.0,
            value=24.0,
            step=0.1,
            help="Body Mass Index"
        )
        
        sex = st.selectbox(
            "Sex",
            options=["Male", "Female"],
            index=1
        )
        
        smoking_status = st.selectbox(
            "Smoking Status",
            options=["Never", "Former", "Current"],
            index=0
        )
        
        family_history = st.selectbox(
            "Family History of Malignancy",
            options=["No", "Yes"],
            index=0
        )
    
    with col2:
        st.subheader("🔬 Clinical Characteristics")
        
        marsh_grade = st.selectbox(
            "Marsh Grade at Diagnosis",
            options=["0", "1", "2", "3a", "3b", "3c"],
            index=4,
            help="Histological grade of intestinal damage (3c is most severe)"
        )
        
        mucosal_healing = st.selectbox(
            "Mucosal Healing on Follow-up",
            options=["Yes", "No"],
            index=0,
            help="Was mucosal healing achieved after gluten-free diet?"
        )
        
        rcd_type = st.selectbox(
            "RCD Type",
            options=["None", "RCD_I", "RCD_II"],
            index=0,
            help="Refractory Celiac Disease type (RCD_II has highest malignancy risk)"
        )
        
        gfd_adherence = st.selectbox(
            "Gluten-Free Diet Adherence",
            options=["Excellent", "Good", "Partial", "Poor"],
            index=1,
            help="How well does the patient follow the gluten-free diet?"
        )
        
        hla_risk = st.selectbox(
            "HLA Risk Level",
            options=["Low", "Medium", "High"],
            index=1,
            help="HLA-DQ2/DQ8 genetic risk level"
        )
    
    st.markdown("---")
    
    # Predict button
    col_button, col_spacer = st.columns([1, 3])
    with col_button:
        predict_button = st.button("🔮 Predict Risk", type="primary", use_container_width=True)
    
    # Make prediction when button is clicked
    if predict_button:
        # Prepare patient data
        patient_data = {
            "age_at_diagnosis": age_at_diagnosis,
            "current_age": current_age,
            "years_of_symptoms_before_diagnosis": years_symptoms,
            "bmi": bmi,
            "followup_years": followup_years,
            "sex": sex,
            "marsh_grade_at_diagnosis": marsh_grade,
            "mucosal_healing_on_followup": mucosal_healing,
            "rcd_type": rcd_type,
            "smoking_status": smoking_status,
            "gfd_adherence": gfd_adherence,
            "family_history_of_malignancy": family_history,
            "hla_risk": hla_risk
        }
        
        # Show spinner while predicting
        with st.spinner("Analyzing patient data..."):
            result, error = predict_risk(patient_data)
        
        if error:
            st.error(f"❌ Error: {error}")
        else:
            # Display results
            st.markdown("---")
            st.subheader("📋 Prediction Results")
            
            risk_class = result['risk_class']
            risk_score = result['risk_score']
            message = result['message']
            
            # Main risk display with color coding
            risk_color = get_risk_color(risk_class)
            st.markdown(
                f"""
                <div style="
                    padding: 20px;
                    border-radius: 10px;
                    border: 3px solid {risk_color};
                    background-color: {risk_color}20;
                    text-align: center;
                    margin: 20px 0;
                ">
                    <h2 style="color: {risk_color}; margin: 0;">
                        {risk_class.upper()} RISK
                    </h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Risk probabilities
            st.markdown("##### Risk Probability Distribution")
            col_low, col_mod, col_high = st.columns(3)
            
            with col_low:
                st.metric(
                    "Low Risk",
                    f"{risk_score[0]:.1%}",
                    delta=None
                )
            
            with col_mod:
                st.metric(
                    "Moderate Risk",
                    f"{risk_score[1]:.1%}",
                    delta=None
                )
            
            with col_high:
                st.metric(
                    "High Risk",
                    f"{risk_score[2]:.1%}",
                    delta=None
                )
            
            # Explanation
            st.markdown("##### Clinical Interpretation")
            st.info(message)
            
            # Additional recommendations
            st.markdown("##### Recommendations")
            if risk_class == "High":
                st.warning("""
                **HIGH RISK patients should:**
                - Be referred to specialist gastroenterology or oncology
                - Undergo comprehensive surveillance including endoscopy
                - Have close monitoring with frequent follow-ups
                - Consider additional diagnostic workup as indicated
                """)
            elif risk_class == "Moderate":
                st.info("""
                **MODERATE RISK patients should:**
                - Continue regular follow-up with gastroenterologist
                - Maintain strict gluten-free diet
                - Monitor for symptom changes
                - Consider periodic surveillance endoscopy
                """)
            else:
                st.success("""
                **LOW RISK patients should:**
                - Continue routine follow-up care
                - Maintain gluten-free diet adherence
                - Monitor for any new symptoms
                - Follow standard surveillance protocols
                """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.9em;">
        <p>
            <strong>Important:</strong> This tool uses synthetic data and is for demonstration purposes only.<br>
            Always consult with qualified healthcare professionals for medical decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #495057; font-size: 0.85em; margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
        <p style="margin: 0; font-weight: 600;">Made for Research by</p>
        <p style="margin: 5px 0 0 0;">Aditya Tiwari • Ayush Yadav • Harshit Somvanshi • Hritik Tiwari</p>
    </div>
    """, unsafe_allow_html=True)



# RUN APP
if __name__ == "__main__":
    main()
