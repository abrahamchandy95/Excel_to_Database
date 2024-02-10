import pandas as pd
import utils as ut
from data_config import SHEET_DICT

def find_non_matched_rows(products_df, price_list_dict):
    """
    Identifies rows in the 'products' DataFrame that did not exactly 
    match any row in the price_list DataFrames.
    """
    desc_column = ut.get_dict_column(products_df)

    # Prepare the products description for matching
    products_prepared = products_df.copy()
    products_prepared['temp_match_col'] = ut.prepare_data_for_matching(products_prepared[desc_column])
    
    # Flag for matched products, initialized to False for all
    matched_products = pd.Series(False, index=products_prepared.index)

    for _, sheet_df in price_list_dict.items():
    
        item_column = ut.get_item_column(sheet_df)
        # Prepare the sheet description for matching
        sheet_df['temp_match_col'] = ut.prepare_data_for_matching(sheet_df[item_column])
        # Identify matched products
        is_matched = products_prepared['temp_match_col'].isin(sheet_df['temp_match_col'])
        matched_products |= is_matched

    # Filter non-matched products
    non_matched_products = products_prepared.loc[~matched_products, products_df.columns]
    return non_matched_products


def match_and_update_price(products_df, price_list_dict):
    """
    This function takes the dataframe and the dictionary of pricelists. 
    For every exact match after data preparation, the row is returned in a dataframe with an updated price.
    """
    eclipse_df = products_df.copy()
    desc_column = ut.get_dict_column(eclipse_df)
    eclipse_df['temp_match_col'] = ut.prepare_data_for_matching(eclipse_df[desc_column])

    matched_products = pd.DataFrame() # Initialize as an empty DataFrame

    for _, sheet_df in price_list_dict.items():
        item_column = ut.get_item_column(sheet_df)
        sheet_df['temp_match_col'] = ut.prepare_data_for_matching(sheet_df[item_column])
        merged_df = pd.merge(eclipse_df, sheet_df, on='temp_match_col', how='left')
        matched_products = pd.concat([matched_products, merged_df], ignore_index=True)

    matched_products = ut.update_price_columns(matched_products)
    matched_products.dropna(subset=[item_column], inplace=True)
    return matched_products[products_df.columns]

def collect_uncreated_items(products_df, price_list_dict):
    """
    This function's purpose is to analyse the price list, check Eclipse's database and find all the items that 
    have not been created yet.
    """
    
    uncreated_items = pd.DataFrame()
    for _, sheet_df in price_list_dict.items():
        item_column = ut.get_item_column(sheet_df)
        non_matched_items = sheet_df[~sheet_df['temp_match_col'].isin(products_df['temp_match_col'])]
        uncreated_items = pd.concat([uncreated_items, non_matched_items], ignore_index=True)
    uncreated_items.dropna(subset=[item_column], inplace=True)
    return uncreated_items.drop(columns=['temp_match_col'])

def find_matches_with_custom_finishes(non_matches_df, price_list_dict):
    """
    Removes all finishes from the price list and then tries to match with the database
    """
    df = non_matches_df.copy()
    desc_column = ut.get_dict_column(df)
    # Prepare for matching
    df['temp_match_col'] = ut.prepare_data_for_matching(df[desc_column])
    unfinished_items = []

    for _, sheet_df in price_list_dict.items():
        item_column = ut.get_item_column(sheet_df)
        # Remove finishes and prepare
        sheet_df['modified_item'] = ut.vectorized_remove_finishes(sheet_df[item_column])
        sheet_df['temp_match_col'] = ut.prepare_data_for_matching(sheet_df['modified_item'])
        unfinished_items.extend(sheet_df['temp_match_col'].unique())
    unique_unfinished_items = set(unfinished_items)

    # Apply custom matching logic
    df['is_potential_match'] = df['temp_match_col'].apply(
        lambda x: ut.is_match_or_substring(x, unique_unfinished_items)
    )
    # Filter non_matched_products
    potential_matches = df[df['is_potential_match']].copy()
    potential_matches.drop(['temp_match_col', 'is_potential_match'], axis=1, inplace=True)

    return potential_matches

def price_custom_finishes(custom_finishes_df, price_list_dict):
    """
    Function that applies pricing to any item with a custom finish.
    Given that we are dealing with items that do not fully match, 
    a dummy column is to be used to fill in the prices, based on custom logic.
    """
    df = custom_finishes_df.copy()
    desc_column = ut.get_dict_column(df)
    df['prepared_desc'] = ut.prepare_data_for_matching(df[desc_column])
    price_dict = {}
    for _, sheet_df in price_list_dict.items():
        # Get the item and price columns
        item_column  = ut.get_item_column(sheet_df)
        price_column = ut.get_price_column(sheet_df)
        if item_column and price_column:
            sheet_df.dropna(subset=[item_column], inplace=True)
                # Prepare data for matching
            sheet_df['prepared_column'] = ut.prepare_data_for_matching(sheet_df[item_column])
            sheet_df['temp_match_col'] = ut.vectorized_remove_finishes(sheet_df['prepared_column'])
            # Update price_dict
            for _, row in sheet_df.iterrows():
                price_dict[row['temp_match_col']] = row[price_column]
            df['Updated LIST PRICE'] = df['prepared_desc1'].apply(lambda x: ut.upcharge_or_standard_charge(x, price_dict))
            
    df = ut.update_price_columns(df)
    df.dropna(subset=['Updated LIST PRICE'], inplace=True)

    # Drop the 'Updated LIST PRICE' column
    df.drop(columns = ['Updated LIST PRICE', 'prepared_desc1'], axis=1, inplace=True)
    return df



