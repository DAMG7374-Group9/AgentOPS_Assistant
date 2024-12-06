import requests
import streamlit as st

from frontend.config import settings
from frontend.utils.auth import set_tokens


def login():
    st.title("User Login")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        response = requests.post(
            f"{settings.BACKEND_URI}/auth/token",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            tokens = response.json()
            set_tokens(tokens)
            st.session_state.logged_in = True
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Login failed")
