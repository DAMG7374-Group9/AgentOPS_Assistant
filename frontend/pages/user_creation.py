import requests
import streamlit as st

from frontend.config import settings


def create_user():
    st.title("User Creation")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    email = st.text_input("Enter Email")
    full_name = st.text_input("Full Name")

    if st.button("Create User"):
        response = requests.post(
            f"{settings.BACKEND_URI}/users/",
            json={
                "username": username,
                "password": password,
                "email": email,
                "full_name": full_name,
            },
        )
        if response.status_code == 201:
            st.success("User created successfully")
        else:
            st.error(f"Error: {response.text}")
