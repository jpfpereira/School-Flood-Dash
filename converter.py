import pandas as pd
import os

# Set the file path
file_path = 'data/Cashflow_Escolas-10.xlsx'
output_dir = 'data'

# Check if the file exists
if not os.path.exists(file_path):
    print(f"Error: The file {file_path} does not exist.")
else:
    # Read the Excel file
    excel_file = pd.ExcelFile(file_path)

    # Get the sheet names
    sheet_names = excel_file.sheet_names

    # Create a dictionary to store dataframes
    dataframes = {}

    # Iterate through each sheet
    for sheet in sheet_names:
        # Read the sheet into a dataframe
        df = pd.read_excel(file_path, sheet_name=sheet)
        
        # Store the dataframe in the dictionary
        dataframes[sheet] = df
        
        # Print the name of the dataframe (sheet name)
        print(f"Dataframe name: {sheet}")

        # Save the dataframe as a CSV file
        csv_file_path = os.path.join(output_dir, f"{sheet}.csv")
        df.to_csv(csv_file_path, index=False)
        print(f"Saved CSV file: {csv_file_path}")

    print(f"\nTotal number of dataframes created and CSV files saved: {len(dataframes)}")