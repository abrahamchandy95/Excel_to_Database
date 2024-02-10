import pandas as pd
import utils as ut
from data_config import REVIVAL_SHEETS, FINISHES, MORTISE_TYPES

def find_and_update_revival_kits(products_df, kit_sheets):
    """
    Runs though Eclipse's Database and finds all products categorized
    by the 'Revival' line. These items are categorized by their special
    Nomenclature. 'PR205TL-HL101-PN' is an example. Uses custom logic
    """
    df = products_df.copy()
    desc_column = ut.get_dict_column(df)
    price_copy = {key: df.copy() for key, df in kit_sheets.items()}
    # Add columns to help with matching
    
    df['left_part'] = df[desc_column].str.extract(r'^([^-\s]+)') # Extract everything before the first '-'
    df['finish'] = df[desc_column].str.extract(r'([^-\s]+)$') # Extract everything after the last '-'
    matched_rows = pd.DataFrame()

    for sheet_name, sheet_df in price_copy.items():
        if sheet_name in REVIVAL_SHEETS:
            item_column = ut.get_item_column(sheet_df)
            sheet_df['left_part'] = sheet_df[item_column].str.split('-').str[0].str.strip()
            sheet_df['finish'] = sheet_df[item_column].str.split('-').str[1].str.strip()

            # Merge on common parts to find matches
            merged_df = df.merge(sheet_df, on=['left_part', 'finish'], how='inner')
            matched_rows = pd.concat([matched_rows, merged_df])
        
    matched_rows = ut.update_price_columns(matched_rows)
    matched_rows = matched_rows[products_df.columns]
    third_unmatched_rows = ut.drop_matching_rows_by_id(df, matched_rows)
    return matched_rows, third_unmatched_rows

def map_metro_items(metro_dict_dfs):
    """
    Creates a consolidated dataframe of all the metro items and strips away the finish.
    In Hamilton's 'Metro' program, upgrading the finish does not merit an upcharge
    """
    mappings = pd.DataFrame(columns=['temp_match_col', 'Updated List Price'])
    metro_price_list = {key: df.copy() for key, df in metro_dict_dfs.items()}
    for _, sheet_df in metro_price_list.items():
        item_column = ut.get_item_column(sheet_df)
        price_column = ut.get_price_column(sheet_df)
        if item_column and price_column:
            sheet_df = sheet_df.dropna(subset=[item_column])
            # Prepare data for matching and remove finishes
            sheet_df['prepared_column'] = ut.prepare_data_for_matching(sheet_df[item_column])
            sheet_df['temp_match_col'] = ut.vectorized_remove_finishes(sheet_df['prepared_column'], FINISHES)
            # Keep only the necessary columns for merging
            temp_df = sheet_df[['temp_match_col', price_column]].rename(columns={price_column: 'Updated List Price'})
            mappings = pd.concat([mappings, temp_df], ignore_index=True)
    # Drop all the duplicates
    mappings = mappings.drop_duplicates(subset=['temp_match_col'])
    return mappings

def categorize_metro_items(metro_df, types_dict):
    """
    Creates a dictionary of dataframes that categorizes metro items
    by function. Each dataframe would contain the price of every skew
    per function. Hamilton has two broad categories: 'Metro' and 'Tubular'
    """
    df = metro_df.copy()
    sorted_keys = sorted(types_dict.keys(), key=len, reverse=True)
    categorized_dict = {}

    for key in sorted_keys:
        # Filter rows containing each key
        condition = df['temp_match_col'].str.contains(key, na=False)
        matched_rows = df[condition]
        if not matched_rows.empty:
            categorized_dict[types_dict[key]] = matched_rows
            # Remove matched rows 
            df = df[~matched_rows]
    return categorized_dict

def merge_and_update_patterns_based_on_description(metro_dict_of_dfs, products_df, col_to_split, mechanism_type):
    """
    This function merges two dataframes and updates them based on common matching patterns found.
    """
    dict_of_dfs = {key: df.copy() for key, df in metro_dict_of_dfs.items()}
    df = products_df.copy()
    df['temp_match_col'] = ut.prepare_data_for_matching(df['temp_match_col'])
    matched_data = pd.DataFrame()
    for _, sheet_df in dict_of_dfs.items():
        temp_df = ut.split_kit_descriptor(sheet_df, col_to_split, mechanism_type)
        price_column = ut.get_price_column(sheet_df)
        temp_df['Updated List Price'] = sheet_df[price_column].values
        # Merge on substrings
        temp_merged = ut.merge_on_patterns(temp_df, df, 'prefix', 'numeric', 'suffix', target_col = 'temp_match_col')
        matched_data = pd.concat([matched_data, temp_merged], ignore_index=True)
    # Update price columns and remove duplicates
    final_data = ut.update_price_columns(matched_data)
    final_data = ut.drop_duplicates_by_price(final_data)
    # Ensure the result has the same columns as the target_data DataFrame
    final_data = final_data[df.columns]
    return final_data









    

