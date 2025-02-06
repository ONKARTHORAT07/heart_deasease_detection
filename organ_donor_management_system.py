import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

st.set_page_config(page_title="Organ Donor Management System", layout="wide")

# Firebase setup
if not firebase_admin._apps:  # Check if Firebase is already initialized
    cred = credentials.Certificate("C:/Users/omkar/heat/serviceAccountKey.json")  # Replace with your Firebase service account key
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://organ-d0d27-default-rtdb.firebaseio.com/'  # Replace with your Firebase database URL
    })

# User role management
role = st.sidebar.selectbox("Login as:", ["User", "Donor", "Doctor"])
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

# Sample authentication data (replace with Firebase authentication in real scenarios)
users = {"user": "user123", "donor": "donor123", "doctor": "doctor123"}

def authenticate(username, password, role):
    if role.lower() in users and users[role.lower()] == password:
        return True
    return False

if login_button:
    if authenticate(username, password, role):
        st.sidebar.success(f"Welcome, {username} ({role})!")
        
        if role == "User":
            st.title("Organ Request Form")
            organ_needed = st.selectbox("Select Organ Needed", ["Kidney", "Liver", "Heart"])
            age = st.number_input("Enter Your Age", min_value=1, max_value=120, step=1)
            blood_type = st.selectbox("Select Blood Type", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            urgency = st.selectbox("Select Urgency Level", ["High", "Medium", "Low"])
            if st.button("Request Organ"):
                request_data = {
                    "username": username,
                    "organ_needed": organ_needed,
                    "age": age,
                    "blood_type": blood_type,
                    "urgency": urgency,
                    "status": "Pending",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                db.reference("organ_requests").push(request_data)
                st.success(f"Organ request for {organ_needed} submitted successfully!")
            st.subheader("Your Organ Requests")
            requests = db.reference("organ_requests").get()
            if requests:
                user_requests = [req for req in requests.values() if req["username"] == username]
                st.write(pd.DataFrame(user_requests))
        
        elif role == "Donor":
            st.title("Organ Donation Form")
            organ = st.selectbox("Select Organ to Donate", ["Kidney", "Liver", "Heart"])
            age = st.number_input("Enter Your Age", min_value=1, max_value=120, step=1)
            blood_type = st.selectbox("Select Blood Type", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            if st.button("Donate Organ"):
                donation_data = {
                    "username": username,
                    "organ": organ,
                    "age": age,
                    "blood_type": blood_type,
                    "approval_status": "Pending",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                db.reference("organ_donations").push(donation_data)
                st.success(f"Thank you for offering to donate your {organ}. It is pending approval by a doctor.")
            st.subheader("Your Donations")
            donations = db.reference("organ_donations").get()
            if donations:
                user_donations = [don for don in donations.values() if don["username"] == username]
                st.write(pd.DataFrame(user_donations))
        
        elif role == "Doctor":
            st.title("Organ Approval Dashboard")
            st.subheader("Pending Organ Requests")
            requests = db.reference("organ_requests").get()
            if requests:
                for key, row in requests.items():
                    if row["status"] == "Pending":
                        st.write(f"Request ID: {key} - User: {row['username']} - Organ Needed: {row['organ_needed']} - Age: {row['age']} - Blood Type: {row['blood_type']} - Urgency: {row['urgency']}")
                        if st.button(f"Approve Request {key}"):
                            db.reference(f"organ_requests/{key}").update({"status": "Approved"})
                            st.success(f"Request {key} approved!")
            st.subheader("Pending Organ Donations")
            donations = db.reference("organ_donations").get()
            if donations:
                for key, row in donations.items():
                    if row["approval_status"] == "Pending":
                        st.write(f"Donor ID: {key} - Donor: {row['username']} - Organ: {row['organ']} - Age: {row['age']} - Blood Type: {row['blood_type']}")
                        if st.button(f"Approve Donation {key}"):
                            db.reference(f"organ_donations/{key}").update({"approval_status": "Approved"})
                            st.success(f"Donation {key} approved!")
    else:
        st.sidebar.error("Invalid username or password. Please try again.")
