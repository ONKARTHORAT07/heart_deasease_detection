import streamlit as st
import numpy as np
# from fpdf import FPDF
from fpdf import FPDF
print("FPDF imported successfully!")

import matplotlib.pyplot as plt
import seaborn as sns
import io
import tempfile
import os

st.set_page_config(page_title="Heart Disease & Symptom Detection App", layout="wide")

st.title("Heart Disease & Symptom Detection App")
st.write("### Predict the likelihood of heart disease and check for possible conditions based on your symptoms.")

# Section 1: Heart Disease Prediction
st.subheader("Heart Disease Risk Assessment")

# User input for health parameters
name = st.text_input("Enter your name")
date_of_check = st.date_input("Date of Check")
age = st.number_input("Age", min_value=1, max_value=120, value=30)
sex = st.selectbox("Sex", ["Male", "Female"])
cp = st.selectbox("Chest Pain Type", ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"])
trestbps = st.number_input("Resting Blood Pressure (mm Hg)", min_value=50, max_value=250, value=120)
chol = st.number_input("Serum Cholesterol (mg/dl)", min_value=100, max_value=600, value=200)
fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", ["Yes", "No"])
restecg = st.selectbox("Resting ECG Results", ["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"])
thalach = st.number_input("Maximum Heart Rate Achieved", min_value=50, max_value=250, value=150)
exang = st.selectbox("Exercise-Induced Angina", ["Yes", "No"])
oldpeak = st.number_input("ST Depression Induced by Exercise", min_value=0.0, max_value=10.0, value=1.0)
slope = st.selectbox("Slope of the Peak Exercise ST Segment", ["Upsloping", "Flat", "Downsloping"])
ca = st.selectbox("Number of Major Vessels Colored by Fluoroscopy", [0, 1, 2, 3, 4])
thal = st.selectbox("Thalassemia", ["Normal", "Fixed Defect", "Reversible Defect"])

# Calculate risk level based on user input
def calculate_risk_level(age, trestbps, chol, thalach, oldpeak):
    risk_score = 0
    if age > 50: risk_score += 1
    if trestbps > 130: risk_score += 1
    if chol > 240: risk_score += 1
    if thalach < 120: risk_score += 1
    if oldpeak > 2.0: risk_score += 1
    
    if risk_score >= 3:
        return "High"
    elif risk_score == 2:
        return "Moderate"
    else:
        return "Low"

risk_level = ""
if st.button("Predict Heart Disease Risk"):
    risk_level = calculate_risk_level(age, trestbps, chol, thalach, oldpeak)
    if risk_level == "High":
        st.error(f"High risk of heart disease detected.")
    elif risk_level == "Moderate":
        st.warning(f"Moderate risk of heart disease.")
    else:
        st.success(f"Low risk of heart disease.")

# Section 2: Symptom Checker
st.subheader("Symptom Checker")

symptoms = st.multiselect("Select your symptoms:", [
    "Fever", "Cough", "Shortness of Breath", "Chest Pain", "Fatigue", "Headache", "Nausea", "Dizziness", "Swelling in Legs", "Palpitations"
])

# Simple symptom-based condition suggestions
def suggest_conditions(symptoms):
    conditions = []
    if "Fever" in symptoms and "Cough" in symptoms and "Shortness of Breath" in symptoms:
        conditions.append("Possible Respiratory Infection (e.g., Pneumonia, COVID-19)")
    if "Chest Pain" in symptoms and "Shortness of Breath" in symptoms:
        conditions.append("Possible Heart Condition (e.g., Angina, Heart Attack)")
    if "Fatigue" in symptoms and "Swelling in Legs" in symptoms:
        conditions.append("Possible Heart Failure")
    if "Headache" in symptoms and "Dizziness" in symptoms:
        conditions.append("Possible Hypertension or Neurological Issue")
    if not conditions:
        conditions.append("No specific condition detected. Please consult a doctor for a detailed diagnosis.")
    return conditions

conditions = []
if st.button("Check Symptoms"):
    conditions = suggest_conditions(symptoms)
    st.write("### Possible Conditions:")
    for condition in conditions:
        st.write(f"- {condition}")

# Visualization Section
st.subheader("Visualization of Risk Factors")

# Plot heart disease risk factors
risk_factors = {
    "Age": age,
    "Resting Blood Pressure": trestbps,
    "Cholesterol": chol,
    "Max Heart Rate": thalach,
    "ST Depression": oldpeak
}

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=list(risk_factors.keys()), y=list(risk_factors.values()), ax=ax)
ax.set_title("Heart Disease Risk Factors")
ax.set_ylabel("Values")
ax.set_xlabel("Factors")
plt.tight_layout()
st.pyplot(fig)

# Temporary file for risk factor chart
tempfile_risk_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
fig.savefig(tempfile_risk_chart.name)
tempfile_risk_chart.close()

# Symptoms distribution pie chart
if symptoms:
    symptom_counts = {symptom: symptoms.count(symptom) for symptom in set(symptoms)}
    fig2, ax2 = plt.subplots()
    ax2.pie(symptom_counts.values(), labels=symptom_counts.keys(), autopct="%1.1f%%", startangle=140)
    ax2.set_title("Symptom Distribution")
    plt.tight_layout()
    st.pyplot(fig2)

# Generate PDF Report
def generate_pdf(name, date_of_check, age, sex, risk_level, symptoms, conditions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Heart Disease & Symptom Detection Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Date of Check: {date_of_check}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
    pdf.cell(200, 10, txt=f"Sex: {sex}", ln=True)
    pdf.cell(200, 10, txt=f"Heart Disease Risk Level: {risk_level}", ln=True)
    pdf.ln(10)
    
    # Add Risk Level Description
    pdf.cell(200, 10, txt="Heart Disease Risk Level Explanation:", ln=True)
    if risk_level == "High":
        pdf.multi_cell(0, 10, txt="High Risk: You have multiple significant risk factors. Immediate medical consultation is recommended.")
    elif risk_level == "Moderate":
        pdf.multi_cell(0, 10, txt="Moderate Risk: You have some risk factors. Consider consulting a doctor for further evaluation.")
    else:
        pdf.multi_cell(0, 10, txt="Low Risk: You have minimal risk factors. Maintain a healthy lifestyle to minimize future risks.")
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Selected Symptoms:", ln=True)
    for symptom in symptoms:
        pdf.cell(200, 10, txt=f"- {symptom}", ln=True)
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Possible Conditions:", ln=True)
    for condition in conditions:
        pdf.cell(200, 10, txt=f"- {condition}", ln=True)
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Risk Factor Visualization:", ln=True)
    pdf.image(tempfile_risk_chart.name, x=10, y=pdf.get_y() + 10, w=180)
    pdf.ln(70)
    
    # pdf.cell(200, 10, txt="Disclaimer: This report is for informational purposes only.", ln=True)
    pdf.output("report.pdf")

# Button to generate the PDF report
if st.button("Generate PDF Report"):
    generate_pdf(name, date_of_check, age, sex, risk_level, symptoms, conditions)
    st.success("PDF report generated successfully!")
    with open("report.pdf", "rb") as file:
        st.download_button("Download Your Report", file, "report.pdf")
