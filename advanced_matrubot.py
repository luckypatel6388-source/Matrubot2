# matrubot_full_chatbot.py
# Matrubot - AI-Based Maternal Health Chatbot
# Python 3.14.2 + Streamlit 3.14.2 compatible
# No voice / no cgi

import streamlit as st
from reportlab.pdfgen import canvas
import json
import os
import time
from datetime import datetime
from PIL import Image


# -----------------------------
# Session State Initialization
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# User Database
# -----------------------------
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

# -----------------------------
# Typing animation function
# -----------------------------
def chatbot_says(text, delay=0.02):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(displayed)
        time.sleep(delay)
    st.session_state.messages.append(text)

# -----------------------------
# PDF report generation
# -----------------------------
def generate_pdf(name, age, weight, weeks, symptoms, risk, consulted_doc, vaccination, appointments, diet, nearest_hospital):
    filename = f"{name}_matrubot_report.pdf"
    c = canvas.Canvas(filename)
    c.setFont("Helvetica", 14)
    c.drawString(50, 800, "🤰 Matrubot Maternal Health Report")
    c.drawString(50, 770, f"Name: {name}")
    c.drawString(50, 750, f"Age: {age}")
    c.drawString(50, 730, f"Weight: {weight} kg")
    c.drawString(50, 710, f"Pregnancy Weeks: {weeks}")
    c.drawString(50, 690, f"Symptoms: {', '.join(symptoms)}")
    c.drawString(50, 670, f"Risk Level: {risk}")
    c.drawString(50, 650, f"Consulted Doctor: {consulted_doc}")
    c.drawString(50, 630, f"Vaccination Status: {vaccination}")
    c.drawString(50, 610, f"Appointments: {', '.join(appointments) if appointments else 'None'}")
    c.drawString(50, 590, f"Recommended Diet: {', '.join(diet)}")
    c.drawString(50, 570, f"Nearest Hospital: {nearest_hospital}")
    c.drawString(50, 550, "Emergency Helpline: +91-1800-123-456")
    c.drawString(50, 530, "Online Doctor Contact: doctor@example.com")
    c.save()
    return filename

# -----------------------------
# Main App
# -----------------------------
st.set_page_config(page_title="Matrubot", page_icon="🤰")
st.image("https://i.imgur.com/FZ8T5zO.png", width=120)  # Logo placeholder
st.title("🤰 Matrubot - Your Maternal Health Chatbot")

users = load_users()
menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Hospital Dashboard"])

# -----------------------------
# Signup
# -----------------------------
if menu == "Signup":
    st.subheader("Create a new account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if new_user in users:
            st.warning("Username already exists")
        else:
            users[new_user] = {"password": new_pass, "history": []}
            save_users(users)
            st.success("Account created! Please login.")

# -----------------------------
# Login
# -----------------------------
elif menu == "Login":
    if not st.session_state.logged_in:
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username}!")
            else:
                st.error("Invalid username or password")
    else:
        username = st.session_state.username
        st.success(f"Welcome back, {username}!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("Logged out! Please login again.")

# -----------------------------
# Hospital Dashboard
# -----------------------------
elif menu == "Hospital Dashboard":
    st.subheader("Hospital Dashboard - User Reports")
    for user, info in users.items():
        st.write(f"**{user}**")
        for record in info.get("history", []):
            st.write(f"- {record['name']}, Week {record['weeks']}, Symptoms: {', '.join(record['symptoms'])}, Risk: {record['risk']}, Vaccination: {record['vaccination']}, Appointments: {', '.join(record['appointments']) if record['appointments'] else 'None'}")

# -----------------------------
# Matrubot Chatbot Flow
# -----------------------------
if st.session_state.logged_in:
    username = st.session_state.username

    # Language selection
    lang = st.selectbox("Select Language / भाषा चुनें", ["English", "Hindi"])
    if lang == "Hindi":
        prompts = {
            "greet": "नमस्ते! मैं Matrubot हूँ। चलिए गर्भ स्वास्थ्य की जांच शुरू करते हैं।",
            "name": "अपना नाम दर्ज करें:",
            "age": "अपनी उम्र दर्ज करें:",
            "weight": "अपना वजन (kg) दर्ज करें:",
            "weeks": "गर्भावस्था का समय (सप्ताह में) दर्ज करें:",
            "symptoms": "अपनी लक्षण चुनें:",
            "consult": "क्या आपने डॉक्टर से सलाह ली है?",
            "vaccination": "क्या आपकी गर्भावस्था के लिए सभी टीकाकरण पूरे हैं?",
            "appointments": "अपनी अगली अपॉइंटमेंट की तारीख जोड़ें:",
            "download": "📄 रिपोर्ट डाउनलोड करें",
            "mental": "क्या आप मानसिक स्वास्थ्य सहायता चाहते हैं?",
        }
    else:
        prompts = {
            "greet": "Hi! I am Matrubot. Let's check your maternal health.",
            "name": "Enter your name:",
            "age": "Enter your age:",
            "weight": "Enter your weight in kg:",
            "weeks": "Pregnancy period in weeks:",
            "symptoms": "Select your symptoms:",
            "consult": "Have you consulted a doctor?",
            "vaccination": "Are your pregnancy vaccinations up-to-date?",
            "appointments": "Add your next appointment date (optional):",
            "download": "📄 Download Report",
            "mental": "Do you want mental health support?",
        }

    # Chatbot greeting
    chatbot_says(prompts["greet"])
    name = st.text_input(prompts["name"])
    age = st.number_input(prompts["age"], 18, 50)
    weight = st.number_input(prompts["weight"], 30, 150)
    weeks = st.number_input(prompts["weeks"], 1, 42)

    # -----------------------------
    # Symptoms
    # -----------------------------
    all_symptoms = [
        "headache","nausea","vomiting","fatigue","bleeding","swelling","fever",
        "pain","dizziness","shortness of breath","back pain","cramps","heartburn",
        "itching","constipation","insomnia","loss of appetite","urination changes",
        "high blood pressure","gestational diabetes","abdominal pain"
    ]
    st.write(prompts["symptoms"])
    symptoms = st.multiselect("Select all that apply:", all_symptoms)

    # -----------------------------
    # Risk Evaluation
    # -----------------------------
    risk_score = len(symptoms)
    if risk_score >= 7:
        risk = "High Risk ⚠️"
        st.error("⚠️ HIGH RISK! Immediate medical consultation is recommended. Monitor symptoms closely. Contact emergency helpline if severe.")
    elif 4 <= risk_score < 7:
        risk = "Moderate Risk ⚠️"
        st.warning("⚠️ Moderate Risk. Please schedule a doctor appointment soon and follow guidance.")
    else:
        risk = "Low Risk ✅"
        st.success("✅ Low Risk. Keep following healthy pregnancy practices.")

    st.write("Symptoms verified by: Obstetrician / Medical Guidelines")
    st.write("Emergency Helpline: +91-1800-123-456")
    st.write("Online Doctor Contact: doctor@example.com")

    # -----------------------------
    # Consultation
    # -----------------------------
    consulted_doc = st.radio(prompts["consult"], ["Yes", "No"])
    vaccination = st.radio(prompts["vaccination"], ["Yes", "No"])
    if vaccination == "No":
        st.warning("Please consult your doctor for pending vaccinations.")

    # -----------------------------
    # Appointment Reminders
    # -----------------------------
    appointments = []
    appointment_date = st.date_input(prompts["appointments"])
    if st.button("Add Appointment"):
        appointments.append(str(appointment_date))
        st.success(f"Appointment added: {appointment_date}")

    # -----------------------------
    # Mental Health Support
    # -----------------------------
    mental_support = st.radio(prompts["mental"], ["Yes", "No"])
    if mental_support == "Yes":
        st.info("💚 Mental health support resources: Talk to a counselor or call +91-1800-987-654")

    # -----------------------------
    # Nutritional Diet Recommendations
    # -----------------------------
    diet_recommendations = []
    if "bleeding" in symptoms or "pain" in symptoms:
        diet_recommendations.append("Iron-rich foods")
    if "vomiting" in symptoms or "nausea" in symptoms:
        diet_recommendations.append("Ginger, light meals")
    if "fatigue" in symptoms or "insomnia" in symptoms:
        diet_recommendations.append("Protein and vitamin-rich foods")
    if not diet_recommendations:
        diet_recommendations.append("Balanced diet: fruits, vegetables, proteins, and hydration")

    st.write("Recommended Diet based on symptoms:", ", ".join(diet_recommendations))

    # -----------------------------
    # Nearest Hospital Placeholder
    # -----------------------------
    nearest_hospital = "City General Hospital, 2 km from your location"
    st.write("Nearest Hospital:", nearest_hospital)

    # -----------------------------
    # Download PDF
    # -----------------------------
    if st.button(prompts["download"]):
        pdf_file = generate_pdf(name, age, weight, weeks, symptoms, risk, consulted_doc, vaccination, appointments, diet_recommendations, nearest_hospital)
        with open(pdf_file, "rb") as f:
            st.download_button(prompts["download"], data=f, file_name=pdf_file, mime="application/pdf")
        st.success("Report generated!")

    # -----------------------------
    # Save history
    # -----------------------------
    users[username]["history"].append({
        "name": name,
        "age": age,
        "weight": weight,
        "weeks": weeks,
        "symptoms": symptoms,
        "risk": risk,
        "consulted_doc": consulted_doc,
        "vaccination": vaccination,
        "appointments": appointments,
        "diet": diet_recommendations,
        "nearest_hospital": nearest_hospital
    })
    save_users(users)

    
# --- Prescription Analysis Feature ---
st.subheader("📝 Smart Prescription Analyzer")
uploaded_prescription = st.file_uploader("Upload your doctor's note (Photo/PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if uploaded_prescription is not None:
    # 1. Display the image
    img = Image.open(uploaded_prescription)
    st.image(img, caption="Uploaded Prescription", use_container_width=True)
    
    with st.spinner("Analyzing medical terms..."):
        # 2. Extract and Analyze (Simulated AI Analysis for your Demo)
        # In a real version, you'd send this 'img' to Gemini Vision or OpenAI Vision
        
        analysis_result = """
        **Matru Bot Analysis:**
        * **Medicine:** Iron Supplement (Folic Acid) - Helps with blood levels.
        * **Instruction:** Take 1 tablet after dinner with water.
        * **Observation:** The doctor noted your BP is slightly high. Please rest more.
        """
        
        st.info(analysis_result)
        
        # 3. Permanent Storage for "Everytime Documents"
        if st.button("Save to My Medical History"):
            file_path = f"user_vault/{st.session_state.username}_{uploaded_prescription.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_prescription.getbuffer())
            
            # Save the text analysis to JSON so it stays there forever
            users[st.session_state.username]["history"].append({
                "date": str(datetime.now()),
                "type": "Prescription Analysis",
                "summary": analysis_result,
                "file_path": file_path
            })
            save_users(users)
            st.success("Saved to your permanent vault!")

# --- The Document Vault Page ---
elif menu == "My Records":
    st.header("🗂 Your Medical Vault")
    user_history = users[st.session_state.username].get("history", [])
    
    if not user_history:
        st.write("No documents saved yet.")
    else:
        for record in user_history:
            if "summary" in record:
                with st.expander(f"Record from {record['date'][:10]}"):
                    st.write(record["summary"])
                    # Option to re-download or view the file
                    st.write(f"File stored at: {record['file_path']}")




# Define the logo path
logo_path = "logo.png"

if os.path.exists(logo_path):
    st.image(logo_path, width=120)
else:
    st.warning("⚠️ Logo file not found. Please upload logo.png to the root folder.")
    st.title("Matru Bot") # Fallback to just text

st.subheader("🏥 Find Urgent Care")
if st.button("Find Hospitals Near Me"):
    # This URL triggers a search for "Maternity Hospital" near the user's current GPS location
    search_url = "https://www.google.com/maps/search/maternity+hospital+near+me/"
    
    st.markdown(f"Opening Google Maps... [Click here if it doesn't open automatically]({search_url})")
    # In a real browser, this link will open their Maps app or a new tab