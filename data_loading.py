import pandas as pd
import numpy as np
import os
from datetime import datetime
import re
from data_config import COLUMN_TYPES, SHEET_DICT

def load_eclipse_products():
    current_directory = os.getcwd()
    csv_file_path = os.path.join(current_directory, "All products information.csv")


    try:
        # Load the CSV file, skip the first 8 rows, and set the 9th row as the header, treat all columns as strings
        products = pd.read_csv(csv_file_path, skiprows = 8, header = 0, dtype = str)

    except UnicodeDecodeError:
          products = pd.read_csv(csv_file_path, skiprows=8, header=0, encoding='ISO-8859-1', dtype = str)
            
    return products

def clean_eclipse_products(df):
     dataframe = df.copy()
     # Dropping and renaming
     dataframe = dataframe.iloc[2:].rename(columns={'DESC': 'Desc5', 'Sta': 'Status'})

     # Ensure the 'Desc5' column is right after 'Desc4', if both exist
     if 'Desc5' in dataframe.columns and 'Desc4' in dataframe.columns:
        cols = dataframe.columns.tolist()
        desc5 = dataframe['Desc5']
        dataframe.drop(labels = ['Desc5'], axis = 1, inplace= True)
        dataframe.insert(cols.index('Desc4')+1, 'Desc5', desc5)

     # Handle non-numeric values from the columns
     dataframe['Status'] = pd.to_numeric(dataframe['Status'], errors = 'coerce').fillna(0).astype(int)
     dataframe['LIST PRICE'] = pd.to_numeric(dataframe['LIST PRICE'], errors = 'coerce')
     dataframe['REP COST'] = pd.to_numeric(dataframe['REP COST'], errors = 'coerce')

     # Drop rows where 'ID' or 'Desc1' is NA
     dataframe.dropna(subset=['ID', 'Desc1'], inplace=True)

         # Apply the column_types to set final dtypes to columns
     for col, dtype in COLUMN_TYPES.items():
        if col in dataframe.columns:
            dataframe[col] = dataframe[col].astype(dtype)

     if 'ID' in dataframe.columns:
        # Drop rows where 'ID' is NA
        dataframe.dropna(subset=['ID'], inplace = True)
        # Convert 'ID' to integers
        dataframe['ID'] = dataframe['ID'].astype(int)

     dataframe = dataframe.replace('(?<!^)\^', '"', regex=True)

     return dataframe.fillna("")

# Function to extract and parse date from filename
def extract_date(filename):
    # Regex pattern to match dates in the format "01.24.2024" or "2024-01-24"
    pattern = r'(\d{2}\.\d{2}\.\d{4})|(\d{4}-\d{2}-\d{2})'
    match = re.search(pattern, filename)
    if match:
        date_str = match.group()
        for fmt in ('%m.%d.%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
            
    return datetime.min

def load_price_list():
    
    # List all files in the current directory
    current_directory = os.getcwd()
    files = os.listdir(current_directory)

    # Filter out all files that contain "Price List"
    price_list_files = [file for file in files if "price list" in file.lower() and file.endswith('.xlsx')]

    # Determine the file with the latest date
    latest_prices = max(price_list_files, key = extract_date, default = None)

    # Read the current file
    if latest_prices:
        price_list = pd.read_excel(os.path.join(current_directory, latest_prices), sheet_name = None)
        print(f"Loaded file: {latest_prices}")
        
    else:
        
        print("No 'Price List' file was found with a valid date, please follow file naming conventions")
    return price_list

def clean_price_list(d_dfs):
    
    dict_of_dfs = d_dfs.copy()
    
    for sheet_name, sheet_df in dict_of_dfs.items():

        first_non_null_column = next((col for col in sheet_df.columns if sheet_df[col].notna().any()), None)

        sheet_df.dropna(subset = [first_non_null_column], inplace = True)
        price_column_set = False

        columns_to_drop = []

        for column in sheet_df.columns:
            if sheet_df[column].dtype == 'float' and not price_column_set:
                sheet_df.rename(columns = {column: 'PRICE'}, inplace = True)
                price_column_set = True
                
            elif sheet_df[column].dtype == 'float' and price_column_set:
                columns_to_drop.append(column)
                
        sheet_df.drop(columns = columns_to_drop, inplace = True)
        sheet_df.dropna(subset = ['PRICE'], inplace = True)
    
    return dict_of_dfs

def filter_price_list(dict_of_dfs, category='individual'):
    return {sheet_name: sheet_df for sheet_name, sheet_df in dict_of_dfs.items() if SHEET_DICT.get(sheet_name) == category}

