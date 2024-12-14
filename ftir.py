import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define predefined peaks for FTIR analysis (simplified version)
peaks = [
    {'wavenumber': 3400, 'label': 'O-H Stretch (Alcohol)'},
    {'wavenumber': 3400, 'label': 'N-H Stretch (Amine)'},
    {'wavenumber': 1700, 'label': 'C=O Stretch (Carbonyl)'},
    {'wavenumber': 2900, 'label': 'C-H Stretch (Alkane)'},
    {'wavenumber': 1650, 'label': 'C=C Stretch (Alkene)'},
    {'wavenumber': 2200, 'label': 'C≡C Stretch (Alkyne)'},
    {'wavenumber': 1100, 'label': 'C-O Stretch (Ether)'},
    {'wavenumber': 1650, 'label': 'C=N Stretch (Imine)'}
]

def run_ftir_analysis(file_path, output_dir):
    # Create directories for saving peak details and figures
    peak_data_dir = os.path.join(output_dir, 'Peak_Details_ftir')
    figures_dir = os.path.join(output_dir, 'Figures_FTIR')
    os.makedirs(peak_data_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # Load Excel file and get all sheet names
    excel_data = pd.ExcelFile(file_path)
    sheet_names = excel_data.sheet_names

    summary_results = []
    composite_fig, composite_ax = plt.subplots(figsize=(12, 8))  # Composite figure for overlay

    # List to store the paths of the figures for display in Streamlit
    figure_paths = []

    # List of colors to use for each individual plot (ensure enough colors for sheets)
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown', 'pink', 'cyan', 'magenta', 'yellow']

    # Loop through each sheet to analyze
    for i, sheet in enumerate(sheet_names):
        # Read only the first two columns, skipping the first row
        try:
            data = pd.read_excel(file_path, sheet_name=sheet, usecols=[0, 1], skiprows=1)
            data.columns = ['Wavenumber(cm-1)', 'Transmittance(%)']  # Rename columns to expected names
        except ValueError:
            print(f"Error reading columns in sheet '{sheet}'. Skipping...")
            continue

        # Check required columns
        if 'Wavenumber(cm-1)' not in data.columns or 'Transmittance(%)' not in data.columns:
            print(f"Missing required columns in sheet '{sheet}'. Skipping...")
            continue

        wavenumber = data['Wavenumber(cm-1)']
        transmittance = data['Transmittance(%)'] 

        # Sort wavenumber in decreasing order (from left to right on the plot)
        sorted_indices = np.argsort(wavenumber)[::-1]  # Sort in descending order
        wavenumber = wavenumber.iloc[sorted_indices]
        transmittance = transmittance.iloc[sorted_indices]

        # Offset each curve for clarity and add to composite plot
        color = colors[i % len(colors)]  # Ensure the same color for both individual and composite plot
        composite_ax.plot(wavenumber, transmittance - i * 20, label=sheet, color=color)  # Matching colors

        # Save individual figure for each sheet
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(wavenumber, transmittance, label=sheet, color=color)

        # Adjust the x-axis range or invert it
        ax.set_xlabel("Wavenumber (cm-1)", fontsize=14)
        ax.set_ylabel("Transmittance (a.u.)", fontsize=14)
        ax.set_title(f"FTIR Spectrum for {sheet}", fontsize=16)

        # Set x-axis limits to show decreasing wavenumber from right to left
        ax.set_xlim(3800, 500)  # Wavenumber from right to left in decreasing order

        ax.legend()

        # Save individual figure
        fig_path = os.path.join(figures_dir, f'FTIR_Spectrum_{sheet}.png')
        fig.savefig(fig_path, dpi=300)
        plt.close(fig)

        # Append the path of the individual figure to the list
        figure_paths.append(fig_path)

        # Detect peaks in specified wavenumbers and save them for each sample
        peak_data = {'Wavenumber': [], 'Transmittance': []}
        for peak in peaks:
            closest_idx = (np.abs(wavenumber - peak['wavenumber'])).argmin()
            peak_data['Wavenumber'].append(wavenumber.iloc[closest_idx])
            peak_data['Transmittance'].append(transmittance.iloc[closest_idx])

        # Save peak details for the current sheet
        peak_df = pd.DataFrame(peak_data)
        peak_file_path = os.path.join(peak_data_dir, f'Peak_Details_{sheet}.csv')
        peak_df.to_csv(peak_file_path, index=False)

        # Append peak details to summary_results
        for _, row in peak_df.iterrows():
            summary_results.append({
                'Sample': sheet,
                'Wavenumber': row['Wavenumber'],
                'Transmittance': row['Transmittance']
            })

    # Customize and save the composite plot showing all sheets
    composite_ax.set_xlabel("Wavenumber (cm-1)", fontsize=14)
    composite_ax.set_ylabel("Transmittance (a.u.)", fontsize=14)
    composite_ax.set_xlim(3800, 500)  # Wavenumber from left to right in decreasing order
    composite_ax.set_ylim(-10, 100)
    composite_ax.set_title("FTIR Spectrum for All Samples (With Vertical Offset)", fontsize=16)

    # Remove ticks and values on the y-axis for clarity
    composite_ax.get_yaxis().set_ticks([])

    # Display the legend with sample names
    composite_ax.legend(loc='upper right', fontsize=12)

    # Save the composite figure only once
    composite_fig_path = os.path.join(figures_dir, 'FTIR_Spectrum_All_Samples_with_Offset.png')
    composite_fig.savefig(composite_fig_path, dpi=300)
    plt.close(composite_fig)

    # Append composite figure path to the list
    figure_paths.append(composite_fig_path)

    # Create a summary DataFrame for all sheets and peaks
    summary_df = pd.DataFrame(summary_results)
    summary_df = summary_df.sort_values(by=['Sample', 'Transmittance'], ascending=[True, False])  # Sort by Sample and Transmittance
    summary_df.to_csv(os.path.join(peak_data_dir, 'FTIR_Peak_Summary.csv'), index=False)

    return summary_df, figure_paths  # Return summary DataFrame and the list of figure paths
