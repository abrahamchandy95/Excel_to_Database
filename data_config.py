# Column types of the products dataframe
COLUMN_TYPES = {
    'Desc1': str,
    'Desc2': str,
    'Desc3': str,
    'Desc4': str,
    'Desc5': str,
    'Status': int,
    'Buy Line': str,
    'Price Line': str,
    'LIST PRICE': float,
    'REP COST': float
}

# Define sheet types for categorizing product sheets
SHEET_DICT = {
    'Cabinet Knobs': 'individual', 
    'Cabinet Pulls': 'individual',
    'Appliance Pulls': 'individual', 
    'Back to Back Appliance Pulls': 'individual',
    'Revival Modern': 'kit', 
    'Revival Modern Special Finish': 'kit', 
    'Revival Classic': 'kit',
    'Revival Classic Special Finish': 'kit', 
    'Revival Components': 'individual',
    'Revival Components Special Fin': 'individual', 
    'Vents & Registers': 'individual',
    'Artisan Door Pulls': 'individual', 
    'Bath Suites': 'individual', 
    'Heritage': 'kit',
    'Metro Knobs + Levers': 'kit', 
    'Metro Tubular': 'kit', 
    'Metro Pocket Door + Thumb Turn': 'kit',
    'Accessories': 'individual',
}


# List of finishes used across all product lines.
FINISHES = (
    'AB', 'BAB', 'BN', 'BRAB', 'BRB', 'BBML', 'BRN', 'DB', 'BP', 'NB', 'MB', 'SN',
    'ORB', 'PW', 'BLN', 'PB', 'PC', 'PN', 'SB', 'UB',
)

# Revival sheet names categorized under different design themes.
REVIVAL_SHEETS = (
    'Revival Classic', 'Revival Classic Special Finish',
    'Revival Modern', 'Revival Modern Special Finish', 
    'Heritage',
)

# Names of sheets related to Metro product lines.
METRO_SHEET_NAMES = (
    'Metro Knobs + Levers', 'Metro Pocket Door + Thumb Turn', 'Metro Tubular',
)
