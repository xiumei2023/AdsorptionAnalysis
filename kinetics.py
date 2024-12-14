import os
import pandas as pd
import streamlit as st
from PIL import Image

# Import analysis functions (ensuring they are in the same directory or proper relative imports)
from kinetics import run_kinetic_fitting
from isotherms import run_isotherm_fitting
from ftir import run_ftir_analysis
from xrd import run_xrd_analysis

# Streamlit Interface
st.title("Data Analysis Interface for Kinetics, Isotherm, FTIR, and XRD")

# File upload and output directory input (default to current directory or allow user input)
uploaded_file = st.file_uploader("Upload your data file (Excel format)", type=["xlsx"], key="file_uploader_main")
output_dir = st.text_input("Enter output directory", "Results", key="output_dir")  # Default to 'Results' directory

# Display selected analysis type
analysis_type = st.sidebar.selectbox("Select Analysis Type", ["Kinetics", "Isotherm", "FTIR", "XRD"], key="analysis_type_select")
st.write(f"Selected Analysis: **{analysis_type}**")

if uploaded_file:
    # Ensure the output directory exists (relative to the current folder or specified)
    os.makedirs(output_dir, exist_ok=True)

    # Create a folder based on the uploaded file's name (without extension)
    file_name_without_extension = os.path.splitext(uploaded_file.name)[0]
    folder_path = os.path.join(output_dir, file_name_without_extension)

    # Ensure the folder for this file exists
    os.makedirs(folder_path, exist_ok=True)

    # Save uploaded file to the newly created folder
    file_path = os.path.join(folder_path, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write(f"File uploaded successfully and saved to {file_path}.")
    
    # Run analysis based on selected type
    if st.button("Run Analysis"):
        summary_df = None  # Initialize placeholder for summary
        figure_paths = []  # List to store figure paths

        try:
            # Based on analysis type, call the corresponding function
            if analysis_type == "Kinetics":
                summary_df, figure_paths = run_kinetic_fitting(file_path, folder_path)

            elif analysis_type == "Isotherm":
                summary_df, figure_paths = run_isotherm_fitting(file_path, folder_path)

            elif analysis_type == "FTIR":
                summary_df, figure_paths = run_ftir_analysis(file_path, folder_path)

            elif analysis_type == "XRD":
                summary_df, figure_paths = run_xrd_analysis(file_path, folder_path)

            # Display figures (individual and composite)
            if figure_paths:
                for fig_path in figure_paths:
                    image = Image.open(fig_path)
                    st.image(image, caption=os.path.basename(fig_path), use_column_width=True)

            # Display fitting results if available
            if summary_df is not None:
                st.write(summary_df)
            else:
                st.error("No results to display.")

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
