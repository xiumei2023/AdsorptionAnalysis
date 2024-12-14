import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lmfit import Model

def run_isotherm_fitting(file_path, output_dir):
    figures_dir = os.path.join(output_dir, 'Figures_Isotherms')
    os.makedirs(figures_dir, exist_ok=True)  # Ensure directory exists
    results_list = []

    # Define Langmuir and Freundlich isotherm models
    def langmuir_isotherm(Ce, q_m, k_L):
        return (q_m * k_L * Ce) / (1 + k_L * Ce)

    def freundlich_isotherm(Ce, k_F, n):
        return k_F * Ce**(1 / n)

    # Load the Excel file and get sheet names
    excel_data = pd.ExcelFile(file_path)
    sheet_names = excel_data.sheet_names

    # List to store the paths of the figures for display in Streamlit
    figure_paths = []

    for sheet in sheet_names:
        # Read data from the first two columns, skip the first row
        data = pd.read_excel(file_path, sheet_name=sheet, skiprows=1, usecols=[0, 1])
        data.columns = ['Ce(mg/L)', 'qe(mg/g)']  # Standard column names

        # Filter out NaN or Inf values
        Ce_data = data['Ce(mg/L)'].dropna().values
        qe_data = data['qe(mg/g)'].dropna().values

        # Check if there are valid data points
        if len(Ce_data) == 0 or len(qe_data) == 0:
            print(f"No valid data in {sheet} after removing NaNs.")
            continue

        # Model setup with lmfit for enhanced control
        langmuir_model = Model(langmuir_isotherm)
        langmuir_params = langmuir_model.make_params(q_m=np.max(qe_data), k_L=0.1)

        freundlich_model = Model(freundlich_isotherm)
        freundlich_params = freundlich_model.make_params(k_F=1.0, n=1.0)

        # Create a new figure per sheet
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(Ce_data, qe_data, color='black', label="Data")

        # Langmuir Model Fitting
        try:
            langmuir_result = langmuir_model.fit(qe_data, Ce=Ce_data, params=langmuir_params)
            ax.plot(Ce_data, langmuir_result.best_fit, 'r-', label=f"Langmuir Fit: q_m={langmuir_result.params['q_m'].value:.2f}, k_L={langmuir_result.params['k_L'].value:.2f}")
            r_squared_langmuir = 1 - (np.sum(langmuir_result.residual**2) / np.sum((qe_data - np.mean(qe_data))**2))
            results_list.append({
                'Sheet': sheet,
                'Model': 'Langmuir',
                'q_m': langmuir_result.params['q_m'].value,
                'k_L': langmuir_result.params['k_L'].value,
                'R^2': r_squared_langmuir
            })

        except Exception as e:
            print(f"Langmuir fitting did not converge for sheet '{sheet}': {e}")

        # Freundlich Model Fitting
        try:
            freundlich_result = freundlich_model.fit(qe_data, Ce=Ce_data, params=freundlich_params)
            ax.plot(Ce_data, freundlich_result.best_fit, 'g--', label=f"Freundlich Fit: k_F={freundlich_result.params['k_F'].value:.2f}, n={freundlich_result.params['n'].value:.2f}")
            r_squared_freundlich = 1 - (np.sum(freundlich_result.residual**2) / np.sum((qe_data - np.mean(qe_data))**2))
            results_list.append({
                'Sheet': sheet,
                'Model': 'Freundlich',
                'k_F': freundlich_result.params['k_F'].value,
                'n': freundlich_result.params['n'].value,
                'R^2': r_squared_freundlich
            })

        except Exception as e:
            print(f"Freundlich fitting did not converge for sheet '{sheet}': {e}")

        # Customize and save each plot as one figure per sheet
        ax.set_xlabel('Ce (mg/L)')
        ax.set_ylabel('qe (mg/g)')
        ax.legend()
        ax.set_title(f'Isotherm Model Fits for {sheet}')
        
        # Save the figure as a PNG file
        fig_path = os.path.join(figures_dir, f'Isotherm_Fit_{sheet}.png')
        fig.savefig(fig_path)
        plt.close(fig)

        # Append the path of the individual figure to the list
        figure_paths.append(fig_path)

    # Convert results to DataFrame
    summary_df = pd.DataFrame(results_list)
    if summary_df.empty:
        print("No valid results were generated.")
        return None, figure_paths  # Return figure paths if no results

    return summary_df, figure_paths  # Return summary DataFrame and the list of figure paths
