# Excel_to_Database
The program is designed to update the supplier's pricing information of all items directly into Eclipse's Database.
It uses the most current data from the Excel spreadsheet. For smooth operation, please use the following guidelines.

## Essential File Preparation
Latest Price List - Ensure that the latest price list is available in the same directory. This must be in .xlsx format
All product information - Alongside the PriceList, there should be a csv file named "All products information.csv"
This file contains comprehensive information about products.

## File Naming
The Price List must contain the keywords "Price" and "List" in its name. The name should also contain the date indicating its recency.
A valid file name can be "Price_List_2024-01-24.xlsx" or "Price List 01.24.2024" Please only use these two date formats
In case multiple price lists exist, the program will select the file with the most recen date in its name to update prices
