import streamlit as st
import pandas as pd
from hashlib import sha256
from PIL import Image, ImageDraw

# Simulated user database
users = {
    "user1": sha256("password1".encode()).hexdigest(),
    "user2": sha256("password2".encode()).hexdigest(),
}

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def authenticate(username, password):
    """Function to authenticate users."""
    if username in users:
        return users[username] == sha256(password.encode()).hexdigest()
    return False

def generate_design(model_name):
    """Function to generate a simple design based on the selected model."""
    # Create a blank image with a simple pattern
    img = Image.new("RGB", (400, 200), color="lightblue")
    draw = ImageDraw.Draw(img)
    draw.text((50, 80), f"Generated Design - {model_name}", fill="black")
    return img

# Login page
if not st.session_state["logged_in"]:
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state["logged_in"] = True
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

# Dashboard after login
else:
    st.title("Dashboard")
    
    # Option to switch between different pages (sections)
    page = st.selectbox("Navigate to", ["Home", "Upload CSV", "Generate Design"])

    if page == "Home":
        st.header("Home")
        st.write("Welcome to the dashboard! Use the navigation menu to access different features.")

    elif page == "Upload CSV":
        st.header("Upload CSV")
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            st.write("CSV file content:")
            st.dataframe(data)

    elif page == "Generate Design":
        st.header("Generate Design")

        # Option to switch between different models within the first page
        model = st.selectbox("Select a model", ["Model A", "Model B", "Model C"])

        if st.button("Generate Design"):
            design_image = generate_design(model)
            st.image(design_image, caption=f"Generated Design using {model}")

    # Logout option
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.success("You have been logged out.")
        st.experimental_rerun()

