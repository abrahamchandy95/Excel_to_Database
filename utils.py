import pandas as pd
import numpy as np

# Functions to find relevant columns in the dataframe
def get_price_column(df):
    """
    Finds the first column in a DataFrame that contains 'price' in its name
    """
    return next((col for col in df.columns if 'price' in col.lower()), None)

def get_item_column(df):
    """
    Finds the first column in a DataFrame that contains 'item' in its name
    """
    return next((col for col in df.columns if 'item' in col.lower()), None)

def get_dict_column(df):
    """
    Finds the first column in a DataFrame that contains 'desc' in its name
    """
    return next((col for col in df.columns if 'desc' in col.lower()), None)

# Function to standardize a column or series
def prepare_data_for_matching(series):
    """
    Standardizes any series or column in a dataframe and allows a limited range of exceptions
    """
    # Fill NaN with empty strings and initialize the column for BTB to be appended later
    series = series.fillna('')
    btb_appended = pd.Series([''] * len(series), index=series.index, dtype = 'object')
    
    # Extract and remove 'BTB', marking rows where 'BTB' was found
    btb_extracted = series.str.contains('BTB')
    series = series.str.replace('BTB', '', regex=False)
    
    # Remove '.' and '-' characters globally
    series = series.str.replace('[.-]', '', regex=True)

    # Adjust the pattern to match 'PH206RR' or 'PH206RL' followed by any alphanumeric character
    series = series.str.replace('PH206R(R|L)(?![a-zA-Z])', 'PH206R', regex=True)

    # Compile finishes and preserved substrings into a single regex pattern
    preserved_substrings = ['RRR', 'PRM', 'PR', 'HL', 'ML', 'PH206R', 'NL', 'OL']
    preserve_pattern = '|'.join(preserved_substrings)
    
    # Mark preserves with unique identifier
    series_marked = series.str.replace(f"({preserve_pattern})", r"__\1__", regex=True)
    
    # For strings starting with 'HL', only remove 'L' or 'R' if not directly following 'HL'
    series_marked = series_marked.str.replace(r'^(HL[^LR]*)(L|R)', r'\1', regex=True)

    # Adjust handedness indicators removal, focusing on generic indicators now
    condition = series_marked.str.contains('HK|HL|PH|ML')
    handedness_indicators = '|'.join(['LHR', 'RHR', 'RL', 'RR'])
    series_marked.loc[condition] = series_marked.loc[condition].str.replace(handedness_indicators, '', regex=True)

    # Restore marked preserves
    series_final = series_marked.str.replace(r"__(.*?)__", r"\1", regex=True)
    
    # Append 'BTB' back to the end where it was extracted
    btb_appended[btb_extracted] = 'BTB'
    series_final += btb_appended

    return series_final

# Function that updates the values of the current price column with the value in the updated price column

def update_price_columns(df):
    """
    Identifying columns that are considered price columns and have a float dtype
    Assuming price columns contain the word 'price' in their name
    """
   
    price_columns = [col for col in df.columns if 'price' in col.lower()and pd.api.types.is_float_dtype(df[col])]

    # Check if there's at least two price columns with float dtype to perform an update
    if len(price_columns) >= 2:
        # Target the first price column for updates
        first_price_col = price_columns[0]
        second_price_col = price_columns[1]

        # Define the condition where the second price column is not null
        condition = df[second_price_col].notna()

        # Perform the update under the condition
        df.loc[condition, first_price_col] = df.loc[condition, second_price_col]

    return df

def is_match_or_substring(item, items_set):
    """
    Checks two strings and identifies if one string is a subset of another
    """
    # Check if the exact item is in the set of items
    if item in items_set:
        return True
    
    # If the item is not exactly in the set, check each item in the set...
    for sub_item in items_set:
        # To see if the current item from the set is a part of the given item
        if sub_item in item:
            return True  # If yes, return True immediately
    
    # If neither the exact match nor any substring match is found, return False
    return False

def custom_finish_upcharge(desc, price_dict):
    """
    If the finish of a product qualifies as custom, an upcharge of 20% is added to the price.
    """
    
    # Filter price_dict for items where the key is a substring of desc
    matches = [price for key, price in price_dict.items() if key in desc]
    # Convert matched prices to numeric values, coercing errors to NaN
    numeric_matches = pd.to_numeric(matches, errors='coerce')
    # Calculate the maximum of the numeric matches, then multiply by 1.2
    
    return np.nanmax(numeric_matches) * 1.2 if not pd.isnull(numeric_matches).all() else np.nan

def upcharge_or_standard_charge(desc, price_dict):
    if desc.endswith('XX'):
        return price_dict.get(desc, np.nan)
    
    else:
        return custom_finish_upcharge(desc, price_dict)
    
def vectorized_remove_finishes(series, finishes):
    """
    Strips a finish from its item.
    """
    # If the series is not a string type, convert it
    if not pd.api.types.is_string_dtype(series):
        series = series.astype(str)
    # Sort finishes by length in descending order to remove longer finishes first
    finishes_sorted = sorted(finishes, key=len, reverse=True)
   
    # Iteratively remove each finish
    for finish in finishes_sorted:
        series = series.str.replace(finish, '', regex=False)

    return series

def drop_matching_rows_by_id(df1, df2):
    """
    Drop rows from df1 that have matching 'ID' values in df2.
    """
    # Identify rows in df1 with 'ID' values that are present in df2
    matching_ids = df1['ID'].isin(df2['ID'])
    # Drop these rows from df1
    df1_filtered = df1[~matching_ids]
    return df1_filtered
