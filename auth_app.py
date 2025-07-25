import streamlit as st
import json
import os

# Path to user data
base_path = os.path.dirname(__file__)
users_file = os.path.join(base_path, "data", "users.json")

# Load user data
def load_users():
    with open(users_file, "r") as f:
        return json.load(f)

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None

# Login UI
st.title("🔐 Clinic Scheduler Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = authenticate(username, password)
    if user:
        st.success("Login successful! Redirecting to schedule...")
        st.session_state.authenticated = True
        st.session_state.role = user["role"]
        st.session_state.username = user["username"]
        st.switch_page("pages/scheduler_app")  # ✅ التعديل هنا
    else:
        st.error("Invalid username or password")
