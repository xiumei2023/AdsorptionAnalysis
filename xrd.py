import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def run_xrd_analysis(file_path, output_dir, peak_prominence=100, num_peaks=15):
    # Create directories for figures and peak details
    figures_dir = os.path.join(output_dir, 'Figures_XRD')
    peak_data_dir = os.path.join(output_dir, 'Peak_Details_XRD')
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(peak_data_dir, exist_ok=True)
    
    summary_results = []
    composite_fig, composite_ax = plt.subplots(figsize=(12, 8))  # Composite figure for overlay

    # Load Excel file and get all sheet names
    excel_data = pd.ExcelFile(file_path)
    sheet_names = excel_data.sheet_names
    colors = ['red', 'blue', 'green', 'purple', 'orange']  # Colors for each sample

    figure_paths = []  # List to store individual figure paths

    # Loop through each sheet for analysis
    for i, sheet in enumerate(sheet_names):
        # Read only the first two columns, skipping the first row
        try:
            data = pd.read_excel(file_path, sheet_name=sheet, usecols=[0, 1], skiprows=1)
            data.columns = ['2Theta', 'Intensity']  # Rename columns to expected names
        except ValueError:
            print(f"Error reading columns in sheet '{sheet}'. Skipping...")
            continue

        # Check required columns
        if '2Theta' not in data.columns or 'Intensity' not in data.columns:
            print(f"Missing required columns in sheet '{sheet}'. Skipping...")
            continue

        theta = data['2Theta']
        intensity = data['Intensity']

        # Individual figure for each sheet
        fig, ax = plt.subplots(figsize=(12, 8))
        color = colors[i % len(colors)]  # Use modulo to cycle through colors

        ax.plot(theta, intensity, color=color, label=sheet)
        ax.set_xlabel("2Theta (degrees)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title(f"XRD Pattern for {sheet}")
        ax.legend()

        # Save individual figure
        fig_path = os.path.join(figures_dir, f'XRD_Pattern_{sheet}.png')
        fig.savefig(fig_path, dpi=300)
        plt.close(fig)

        # Add the figure path to the list
        figure_paths.append(fig_path)

        # Add to composite plot with vertical offset
        offset_intensity = intensity + i * 1000
        composite_ax.plot(theta, offset_intensity, color=color, label=sheet)

        # Detect peaks in the intensity data
        peaks, properties = find_peaks(intensity, prominence=peak_prominence)
        prominent_peaks = peaks[np.argsort(properties['prominences'])[-num_peaks:]]  # Select the most prominent peaks

        # Save peak details to a DataFrame, sorted by Intensity in descending order
        peak_details = pd.DataFrame({
            'Sample': sheet,
            '2Theta': theta.iloc[prominent_peaks].values,
            'Intensity': intensity.iloc[prominent_peaks].values
        }).sort_values(by='Intensity', ascending=False)  # Sort by intensity descending

        # Save sorted peak details for each sheet to CSV
        peak_details.to_csv(os.path.join(peak_data_dir, f'Peak_Details_{sheet}.csv'), index=False)

        # Append sorted data to summary_results
        summary_results.extend(peak_details.to_dict(orient='records'))

    # Customize composite plot
    composite_ax.set_xlabel("2Theta (degrees)", fontsize=14)
    composite_ax.set_ylabel("Intensity (a.u.)", fontsize=14)
    composite_ax.legend(loc='upper right', fontsize=10)
    composite_ax.set_title("XRD Patterns for Samples (With Vertical Offset)", fontsize=16)

    # Remove ticks and values on the y-axis for composite plot
    composite_ax.get_yaxis().set_ticks([])

    # Save composite figure
    composite_fig_path = os.path.join(figures_dir, 'XRD_Pattern_All_Samples_with_Offset.png')
    composite_fig.savefig(composite_fig_path, dpi=300)
    plt.close(composite_fig)

    # Append composite figure path to the list of figure paths
    figure_paths.append(composite_fig_path)

    # Create summary DataFrame for all sheets and peaks, sorted by Sample and Intensity descending
    summary_df = pd.DataFrame(summary_results)
    summary_df = summary_df.sort_values(by=['Sample', 'Intensity'], ascending=[True, False])  # Sort by Sample and Intensity
    summary_df.to_csv(os.path.join(peak_data_dir, 'XRD_Peak_Summary.csv'), index=False)

    return summary_df, figure_paths  # Return summary DataFrame and the list of figure paths
