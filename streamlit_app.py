import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import io
import os
from PIL import Image, ImageDraw
from hashlib import sha256
from keras.models import load_model
from phidl import Device
import antenna_class_single  # Ensure this module is accessible

# Load the trained model
model = load_model('rayce_v1/inverse_design_model.keras')

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

def generate_design(antenna):
    """Function to generate a design based on the antenna object."""
    canvas_size = 100
    canvas = np.zeros((canvas_size, canvas_size))
    center = canvas_size // 2

    for size, frame_width, gap_size, gap_position in antenna.resonators:
        # Create resonator matrix with a gap
        resonator_matrix = antenna.create_resonator_matrix_with_gap(size, frame_width, gap_size, gap_position)
        
        # Calculate top-left corner of the resonator
        start_x = center - size // 2
        start_y = center - size // 2
        
        # Place the resonator matrix onto the canvas
        canvas[start_x:start_x+size, start_y:start_y+size] = np.maximum(canvas[start_x:start_x+size, start_y:start_y+size], resonator_matrix)
    
    # Plotting
    fig, ax = plt.subplots()
    ax.imshow(canvas, cmap='gray')
    ax.set_title("Generated Design")
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    return buf

def create_gds_file(antenna):
    """Function to create GDS file from the antenna object."""
    D = Device('SplitRingResonators')
    for size, frame_width, gap_size, gap_position in antenna.resonators:
        coords = antenna.create_resonator_polygon(size, frame_width, gap_size, gap_position)
        D.add_polygon(coords, layer=1)
    
    # Save to a temporary file
    gds_filename = 'output.gds'
    D.write_gds(gds_filename)
    return gds_filename

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
    # Sidebar menu with additional functionalities
    st.sidebar.title("Menu")
    menu_options = ["Main Page", "Feature 1", "Feature 2", "Logout"]
    choice = st.sidebar.radio("Navigate", menu_options)

    if choice == "Main Page":
        st.title("Dashboard")
        st.write("Welcome to the dashboard! You can upload a CSV file and generate a design.")

        # Option to switch between different models within the first page
        model_name = st.selectbox("Select a model", ["Model A", "Model B", "Model C"])

        # CSV file upload
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file is not None:
            # Read and display the CSV file
            df = pd.read_csv(uploaded_file)
            st.write("CSV file content:")
            st.dataframe(df)

            # Button to generate a design
            if st.button("Generate Design"):
                # Preprocess the data for the model
                data = df.values
                # Make sure data is in the correct shape
                data = data.reshape((1, -1))
                model_output = model.predict(data)

                # Create the antenna instance from model output
                antenna = antenna_class_single.Resonator(
                    resonators=[[
                        # Use model_output values appropriately
                        50,  # size
                        4,   # frame_width
                        3,   # gap_size
                        'top'  # gap_position
                    ]]
                )

                # Generate design from model output
                design_image = generate_design(antenna)

                # Display the design image
                st.image(design_image, caption="Generated Design", use_column_width=True)

                # Button to download GDS file
                if st.button("Download GDS File"):
                    gds_filename = create_gds_file(antenna)
                    with open(gds_filename, 'rb') as f:
                        gds_data = f.read()
                    st.download_button(
                        label="Download GDS File",
                        data=gds_data,
                        file_name='output.gds',
                        mime='application/octet-stream'
                    )
        else:
            st.info("Please upload a CSV file to proceed.")

    elif choice == "Feature 1":
        st.title("Feature mrdka")
        st.write("This is Feature 1. Add your content here.")

    elif choice == "Feature 2":
        st.title("Feature 2")
        st.write("This is Feature 2. Add your content here.")

    elif choice == "Logout":
        st.session_state["logged_in"] = False
        st.success("You have been logged out.")
        st.experimental_rerun()
