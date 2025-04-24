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
import antenna_class_bowtie  # Import the Bowtie class module
from io import BytesIO
import tempfile

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



def create_gds_file(antenna):
    """Function to create GDS file from the antenna object."""
    D = Device('SplitRingResonators')
    for size, frame_width, gap_size, gap_position in antenna.resonators:
        coords = antenna.create_resonator_polygon(size, frame_width, gap_size, gap_position)
        D.add_polygon(coords, layer=1)
    
    # Use a temporary file to store the GDS file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".gds")
    D.write_gds(temp_file.name)
    return temp_file.name  # Return the temporary file path


def create_bowtie_gds_file(bowtie):
    """Function to create GDS file from the bowtie object."""
    D = Device('BowtieAntenna')
    coords = bowtie.create_bowtie_polygon()
    D.add_polygon(coords, layer=1)
    
    # Save to a temporary file
    gds_filename = 'bowtie_output.gds'
    D.write_gds(gds_filename)
    st.write("Ty mrdko!")

    return gds_filename

# Function to load the model based on the selected model name
@st.cache_resource
def load_model_by_name(model_name):
    """Function to load the model based on the model name."""
    if model_name == "Single split ring model":
        return load_model('models/inverse_design_model.h5', compile=False)
    elif model_name == "Double split ring model":
        return load_model('models/inverse_design_model.h5', compile=False)
    else:
        st.error("Invalid model selected.")
        return None

# Login page
if not st.session_state["logged_in"]:
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state["logged_in"] = True
            st.success("Login successful!")
            st.experimental_set_query_params()
      #      st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

# Dashboard after login
else:
    # Sidebar menu with additional functionalities
    st.sidebar.title("Menu")
    menu_options = ["Split-ring resonator generation", "Bowtie resonance", "Logout"]
    choice = st.sidebar.radio("Navigate", menu_options)

    if choice == "Split-ring resonator generation":
        st.title("Split-ring resonator generation")
        st.write("You can upload a CSV file and generate a design.")

        # Option to switch between different models within the first page
        model_name = st.selectbox("Select a model", ["Single split ring model", "Double split ring model"])

        # Load the selected model
        model = load_model_by_name(model_name)
        st.write("Model loaded.")

        # CSV file upload
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file is not None:
        # Read the CSV file
            df = pd.read_csv(uploaded_file, header=None)
            if not df.select_dtypes(include=['number']).empty:
                fig, ax = plt.subplots()
  
                # Plot the first two numeric columns as an example
                numeric_columns = df.select_dtypes(include=['number']).columns
                if len(numeric_columns) == 2:
                    ax.plot(df[numeric_columns[0]], df[numeric_columns[1]])
                    ax.set_xlabel('Frequency [THz]')
                    ax.set_ylabel('T')
                    ax.legend()
                    st.pyplot(fig)
                else:
                    try:
                        df.iloc[:, 0] = df.iloc[:, 0].str.strip('[]').astype(float)
                        df.columns = ['X', 'Y']
                        ax.plot(df['X'], df['Y'])
                        ax.set_xlabel('Frequency [THz]')
                        ax.set_ylabel('T')
                        ax.legend()
                        df = df.set_index('X')
                        st.pyplot(fig)

                    except:
                        st.write("The CSV file does not have enough numeric columns to plot.")

            # Button to generate a design
            if st.button("Generate Design"):
                if model is not None:
                    # Preprocess the data for the model
                    df = df.T
                    df.columns = [f'Transmission_{i}' for i in range(df.shape[1])]
                    data = df.values
                    model_output = model.predict(data)

                    if model_name == "Single split ring model":
                        # Create the antenna instance from model output
                        antenna = antenna_class_single.Resonator(
                            resonators=[[
                                # Use model_output values appropriately
                                50,
                                4,
                                3,
                           #     int(model_output[0][0]),  # size
                           #     int(model_output[0][1]),  # frame_width
                           #     int(model_output[0][2]),  # gap_size
                           #     int(model_output[0][3])  # gap_position
                                'top'
                            ]]
                        )

                    elif model_name == "Double split ring model":
                        # Create the antenna instance from model output
                        antenna = antenna_class_double.Resonator(
                            resonators=[[
                                # Use model_output values appropriately
                                int(model_output[0][0]),  # size
                                int(model_output[0][1]),  # frame_width
                                int(model_output[0][2]),  # gap_size
                                int(model_output[0][3]),  # gap_position
                                int(model_output[1][0]),  # size
                                int(model_output[1][1]),  # frame_width
                                int(model_output[1][2]),  # gap_size
                                int(model_output[1][3]),  # gap_position
                            ]]
                        )

                    # Generate design from model output
                 #   design_image = generate_design(antenna)
                    design_image = antenna.plot_concentric_antenna(100)

                    # Store the antenna and GDS data in session state
                    st.session_state["design_image"] = design_image
                    st.session_state["antenna"] = antenna
                    st.session_state["gds_data"] = create_gds_file(antenna)
                    
            # Display the design image if it exists in session state
            if "design_image" in st.session_state:
                st.image(st.session_state["design_image"], caption="Generated Resonator Design", use_column_width=True)
            else:
                st.info("Please generate a design to view it.")


            # Ensure the design persists for download
            if "gds_data" in st.session_state:
                # Allow GDS file generation and download
                st.download_button(
                    label="Download GDS File",
                    data=st.session_state["gds_data"],
                    file_name="output.gds",
                    mime="application/octet-stream"
                )
            else:
                st.info("Please generate a design first.")

        else:
            st.info("Please upload a CSV file to proceed.")

    elif choice == "Bowtie resonance":
        st.title("Bowtie resonance")
        st.write("This is Feature 1. Add your content here.")

                # Input for resonance frequency
        resonance_thz = st.text_input("Enter resonance frequency (THz)", value="0.5")

        if st.button("Generate Bowtie Design"):
            try:
            # Placeholder logic for generating bowtie parameters
            # Replace this with actual model inference or calculation
                length = float(resonance_thz) * 50  # Example calculation
                width = float(resonance_thz) * 10   # Example calculation

                # Generate a bowtie antenna object with the calculated parameters
                bowtie = antenna_class_single.antenna_class_bowtie(
                    length=int(length),
                    width=int(width)
                )

                # Generate bowtie design image
                design_image = generate_bowtie_design(bowtie)

                # Display the design image
                st.image(design_image, caption="Generated Bowtie Antenna Design", use_column_width=True)

            # Button to download GDS file
                if st.button("Download Bowtie GDS File"):
                    gds_filename = create_bowtie_gds_file(bowtie)
                    with open(gds_filename, 'rb') as f:
                        gds_data = f.read()
                    st.download_button(
                        label="Download Bowtie GDS File",
                        data=gds_data,
                        file_name='bowtie_output.gds',
                        mime='application/octet-stream'
                    )
            except ValueError:
                st.error("Invalid resonance frequency. Please enter a valid numeric value.")

  # elif choice == "Feature 2":
  #      st.title("Feature 2")
  #      st.write("This is Feature 2. Add your content here.")

    elif choice == "Logout":
        st.session_state["logged_in"] = False
        st.success("You have been logged out.")
       # st.experimental_rerun()
