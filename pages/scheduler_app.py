
import streamlit as st
import json
import random
import pandas as pd
import pdfkit
import tempfile
import datetime
import os

# Check auth
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Unauthorized access. Please login first.")
    st.stop()

# Paths
base_path = os.path.dirname(__file__)
staff_path = os.path.join(base_path, "staff.json")
config_path = os.path.join(base_path, "config.json")
users_file = os.path.join(base_path, "users.json")

# Load config and staff
with open(staff_path) as f:
    staff_data = json.load(f)
nurses = [n for n in staff_data["nurses"] if n.lower() not in ["tombi", "jennifer"]]
technicians = [t for t in staff_data["technicians"] if t.lower() not in ["tombi", "jennifer"]]

with open(config_path) as f:
    config = json.load(f)

schedule_config = config["schedule"]
staffing_rules = config["staffing_rules"]

# UI
st.title("📅 Weekly Clinic Scheduler")

# Admin user management section
if st.session_state.role == "admin":
    with st.expander("➕ Add New User"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["viewer", "admin"])
        if st.button("Add User"):
            with open(users_file, "r") as f:
                users = json.load(f)
            if any(u["username"] == new_username for u in users):
                st.error("❌ Username already exists.")
            else:
                users.append({
                    "username": new_username,
                    "password": new_password,
                    "role": new_role
                })
                with open(users_file, "w") as f:
                    json.dump(users, f, indent=2)
                st.success("✅ User added successfully.")

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
        config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
        pdfkit.from_string(html_content, tmpfile.name, configuration=config)
        with open(tmpfile.name, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="clinic_schedule.pdf")
