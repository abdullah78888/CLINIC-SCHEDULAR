
import streamlit as st
import json
import random
import pandas as pd
import pdfkit
import tempfile
import datetime
import os

# Paths
users_file = "data/users.json"
staff_path = "data/staff.json"
config_path = "data/config.json"

# Authentication
def load_users():
    with open(users_file, "r") as f:
        return json.load(f)

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None

# Load config and staff
with open(staff_path) as f:
    staff_data = json.load(f)
nurses = [n for n in staff_data["nurses"] if n.lower() not in ["tombi", "jennifer"]]
technicians = [t for t in staff_data["technicians"] if t.lower() not in ["tombi", "jennifer"]]

with open(config_path) as f:
    config = json.load(f)

schedule_config = config["schedule"]
staffing_rules = config["staffing_rules"]

# Login UI
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Clinic Scheduler Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.role = user["role"]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# Main App
st.title("📅 Weekly Clinic Scheduler")

start_date = st.date_input("Select the start date (Sunday):", datetime.date.today())

if st.button("Generate Schedule"):
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    periods = ["AM", "PM"]
    data = []

    used_staff_daily = {}

    for i, day in enumerate(days):
        current_date = start_date + datetime.timedelta(days=i)
        used_staff_daily[day] = {"AM": set(), "PM": set()}

        for period in periods:
            clinics = schedule_config.get(day, {}).get(period, [])
            for clinic_name in clinics:
                clinic_key = clinic_name.upper()
                rule = staffing_rules.get(clinic_key, staffing_rules["DEFAULT"])

                assigned_nurses = []
                assigned_techs = []

                for _ in range(rule["nurses"]):
                    available_nurses = [n for n in nurses if n not in used_staff_daily[day][period]]
                    if available_nurses:
                        selected = random.choice(available_nurses)
                        assigned_nurses.append(selected)
                        used_staff_daily[day][period].add(selected)
                    else:
                        assigned_nurses.append("Not Assigned")

                for _ in range(rule.get("technicians", 0)):
                    available_techs = [t for t in technicians if t not in used_staff_daily[day][period]]
                    if available_techs:
                        selected = random.choice(available_techs)
                        assigned_techs.append(selected)
                        used_staff_daily[day][period].add(selected)
                    else:
                        assigned_techs.append("Not Assigned")

                data.append({
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Day": day,
                    "Period": period,
                    "Clinic": clinic_name,
                    "Nurses": ", ".join(assigned_nurses),
                    "Technicians": ", ".join(assigned_techs)
                })

    df = pd.DataFrame(data)

    st.subheader("📋 Generated Schedule")
    st.dataframe(df, use_container_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        html_content = df.to_html(index=False)
        config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        pdfkit.from_string(html_content, tmpfile.name, configuration=config)
        with open(tmpfile.name, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="clinic_schedule.pdf")
