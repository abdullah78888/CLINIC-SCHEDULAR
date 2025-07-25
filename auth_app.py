import streamlit as st
import json
import os

users_file = os.path.join("data", "users.json")

def load_users():
    with open(users_file, "r") as f:
        return json.load(f)

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

st.title("🔐 Clinic Scheduler Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = authenticate(username, password)
    if user:
        st.success(f"Welcome {user['username']}! Redirecting...")
        st.switch_page("scheduler_app")  # التعديل هنا
    else:
        st.error("Invalid username or password.")