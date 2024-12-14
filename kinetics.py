import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lmfit import Model

def run_kinetic_fitting(file_path, output_dir):
    figures_dir = os.path.join(output_dir, 'Figures_Kinetics')
    os.makedirs(figures_dir, exist_ok=True)  # Create directory for figures if it doesn't exist
    results_list = []
    
    # Define pseudo-first-order and pseudo-second-order models
    def pseudo_first_order(t, q_e, k1):
        return q_e * (1 - np.exp(-k1 * t))

    def pseudo_second_order(t, q_e, k2):
        return (q_e**2 * k2 * t) / (1 + q_e * k2 * t)

    # Load the Excel file and get sheet names
    excel_data = pd.ExcelFile(file_path)
    sheet_names = excel_data.sheet_names

    # List to store the paths of the figures for display in Streamlit
    figure_paths = []

    for sheet in sheet_names:
        # Read data from the first two columns, skip the first row
        data = pd.read_excel(file_path, sheet_name=sheet, skiprows=1, usecols=[0, 1])
        data.columns = ['time(min)', 'qt(mg/g)']
        
        # Ensure required columns are present
        t_data = data['time(min)'].dropna().values
        q_data = data['qt(mg/g)'].dropna().values
        
        # Model setup with lmfit for enhanced control
        first_order_model = Model(pseudo_first_order)
        first_order_params = first_order_model.make_params(q_e=np.max(q_data), k1=0.1)
        
        second_order_model = Model(pseudo_second_order)
        second_order_params = second_order_model.make_params(q_e=np.max(q_data), k2=0.001)
        
        # Create a new figure only once per sheet
        fig, ax = plt.subplots(figsize=(8, 6))  # Set figure size for consistency
        ax.plot(t_data, q_data, 'bo', label="Data")

        try:
            # Fit and plot pseudo-first-order model
            first_order_result = first_order_model.fit(q_data, t=t_data, params=first_order_params)
            ax.plot(t_data, first_order_result.best_fit, 'r-', label=f"1st Order Fit: q_e={first_order_result.params['q_e'].value:.2f}, k1={first_order_result.params['k1'].value:.2f}")
            r_squared_1st = 1 - first_order_result.residual.var() / np.var(q_data)
            results_list.append({
                'Sheet': sheet, 
                'Model': 'Pseudo First Order', 
                'q_e': first_order_result.params['q_e'].value, 
                'k': first_order_result.params['k1'].value, 
                'R^2': r_squared_1st
            })
            
            # Fit and plot pseudo-second-order model
            second_order_result = second_order_model.fit(q_data, t=t_data, params=second_order_params)
            ax.plot(t_data, second_order_result.best_fit, 'g--', label=f"2nd Order Fit: q_e={second_order_result.params['q_e'].value:.2f}, k2={second_order_result.params['k2'].value:.2f}")
            r_squared_2nd = 1 - second_order_result.residual.var() / np.var(q_data)
            results_list.append({
                'Sheet': sheet, 
                'Model': 'Pseudo Second Order', 
                'q_e': second_order_result.params['q_e'].value, 
                'k': second_order_result.params['k2'].value, 
                'R^2': r_squared_2nd
            })

        except Exception as e:
            print(f"Error fitting model for sheet '{sheet}': {e}")
            continue

        # Customize and save each plot as one figure per sheet
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Adsorption Amount (qt)')
        ax.legend()
        ax.set_title(f'Kinetic Model Fits for {sheet}')
        
        # Save the figure as a PNG file
        fig_path = os.path.join(figures_dir, f'Kinetic_Fit_{sheet}.png')
        fig.savefig(fig_path)
        plt.close(fig)  # Close the figure after saving to avoid duplicates

        # Append the path of the individual figure to the list
        figure_paths.append(fig_path)

    # Convert results to DataFrame
    summary_df = pd.DataFrame(results_list)
    if summary_df.empty:
        print("No valid results were generated.")
        return None, figure_paths  # Return figure paths if no results

    return summary_df, figure_paths  # Return summary DataFrame and the list of figure paths
