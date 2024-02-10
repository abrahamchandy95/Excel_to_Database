import os
from datetime import datetime
import pandas as pd

from data_loading import (
    clean_eclipse_products, load_eclipse_products,
    clean_price_list, load_price_list, filter_price_list
)
import basic_matching as bm
import kit_matching as km
from data_config import (
    METRO_SHEET_NAMES, MORTISE_TYPES, TUBULAR_TYPES,
    FINISHES
)
from utils import (
    drop_matching_rows_by_id, vectorized_remove_finishes
)

def main():

    # Load and clean the products DataFrame
    products = clean_eclipse_products(load_eclipse_products())

    # Load and clean the price list dictionary of DataFrames
    price_list = clean_price_list(load_price_list())

    # Filter the price_list dictionary of dataframes
    non_kit_price_list = filter_price_list(price_list, 'individual')
    kit_price_list = filter_price_list(price_list, 'kit')

    # The first update isolates direct matches between Eclipse's 
    # Database and the price list, directly feeding in the updated 
    # price.
    first_update = bm.match_and_update_price(products, price_list)

    # Process custom finishes
    unmatched_rows = bm.find_unmatched_rows(products, price_list)
    custom_finished_matches = bm.find_matches_with_custom_finishes(unmatched_rows, non_kit_price_list)
    custom_finished_products = bm.price_custom_finishes(custom_finished_matches, non_kit_price_list)
    second_update = pd.concat([first_update, custom_finished_products], ignore_index=True)
    second_unmatched_rows = drop_matching_rows_by_id(unmatched_rows, second_update)

    # Add 'Revival' Kits and the third set of unmatched rows
    revival_kits, third_unmatched_rows = km.find_and_update_revival_kits(second_unmatched_rows, kit_price_list)
    third_update = pd.concat([second_update, revival_kits], ignore_index=True)

    # Adding 'Metro' Kits
    metro_sheets = {name: kit_price_list[name] for name in METRO_SHEET_NAMES}
    # A map of 'Metro' items, that shows item without finish and the price
    metro_items = km.map_metro_items(metro_sheets)
    # Split Metro Mortise items into a dictionary of dataframes
    metro_mortise_categorized = km.categorize_metro_items(metro_items, MORTISE_TYPES)
    # Update Metro Mortise sets and update the main df
    metro_mortise_sets = km.merge_and_update_patterns_based_on_description(
        metro_mortise_categorized, third_unmatched_rows, 'temp_match_col', MORTISE_TYPES)
    
    fourth_update = pd.concat(third_update, metro_mortise_sets, ignore_index=True)
    fourth_unmatched_rows = drop_matching_rows_by_id(third_unmatched_rows, fourth_update)
    # Metro Tubular Kits
    metro_tubular_categorized = km.categorize_metro_items(metro_items, TUBULAR_TYPES)
    metro_tubular_df = kit_price_list['Metro Tubular']
    metro_tubular_df['temp_match_col'] = vectorized_remove_finishes(metro_tubular_df['temp_match_col'], FINISHES)
    metro_tubular_updated = km.merge_and_update_patterns_based_on_description(
    metro_tubular_categorized,  # Dictionary of DataFrames for tubular items
    fourth_unmatched_rows,  # DataFrame to match against
    'temp_match_col',  # Column to split in the dictionary of DataFrames
    TUBULAR_TYPES  # Mechanism type dictionary for splitting
)
    fifth_update = pd.concat([fourth_update, metro_tubular_updated], ignore_index=True)
    #REMOVE DPAMS
    mask = ~fifth_update['Desc1'].str.contains('DPAM', na=False)
    final_update = fifth_update[mask]
    # Items not created yet from the price list (individual sheets only)
    uncreated_items = bm.collect_uncreated_items(products, non_kit_price_list)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    new_filename = f"Updated Prices to be uploaded_{timestamp}.csv"
    final_update.to_csv(new_filename)
    create_file = f"Create these Products_{timestamp}.csv"
    uncreated_items.to_csv(create_file)

    print("Script completed and files saved.")


if __name__ == '__main__':
    main()


