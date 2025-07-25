
import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Paths
data_path = Path(__file__).parent / "data"
config_path = data_path / "config.json"
staff_path = data_path / "staff.json"

# Load configuration
with open(config_path) as f:
    config = json.load(f)

# Load staff
with open(staff_path) as f:
    staff_data = json.load(f)

nurses = staff_data["nurses"]
technicians = staff_data["technicians"]

# Generate dates for the week
def generate_week_dates(start_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    dates = []
    for i in range(5):  # Sunday to Thursday
        day = start_date + timedelta(days=i)
        dates.append(day.strftime("%Y-%m-%d"))
    return dates

# Build schedule dataframe
def generate_schedule(start_date_str):
    schedule = []
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    periods = ["AM", "PM"]
    week_dates = generate_week_dates(start_date_str)

    used_staff = set()

    for i, day in enumerate(days):
        for period in periods:
            clinics = config["schedule"].get(day, {}).get(period, [])
            for clinic in clinics:
                key = f"{day}_{period}_{clinic}"
                rule = config["staffing_rules"].get(key, config["staffing_rules"].get("DEFAULT", {"nurses": 1, "technicians": 0}))
                assigned_nurses = []
                assigned_techs = []

                for _ in range(rule["nurses"]):
                    available = [n for n in nurses if n not in used_staff]
                    if available:
                        selected = random.choice(available)
                        assigned_nurses.append(selected)
                        used_staff.add(selected)
                    else:
                        assigned_nurses.append("Not Assigned")

                for _ in range(rule["technicians"]):
                    available = [t for t in technicians if t not in used_staff]
                    if available:
                        selected = random.choice(available)
                        assigned_techs.append(selected)
                        used_staff.add(selected)
                    else:
                        assigned_techs.append("Not Assigned")

                schedule.append({
                    "Date": week_dates[i],
                    "Day": day,
                    "Period": period,
                    "Clinic": clinic,
                    "Nurses": ", ".join(assigned_nurses),
                    "Technicians": ", ".join(assigned_techs)
                })

    return pd.DataFrame(schedule)

# Streamlit UI
st.title("🗓️ Weekly Clinic Schedule")

start_date = st.date_input("Select the week start date (Sunday):")
if st.button("Generate Schedule") and start_date:
    df = generate_schedule(str(start_date))
    st.dataframe(df)

    with st.expander("📥 Download Schedule as Excel"):
        import io
        with io.BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Schedule")
            st.download_button(
                label="Download Excel File",
                data=buffer.getvalue(),
                file_name="clinic_schedule.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
