# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 16:50:09 2023

@author: Franco
"""

# Check certificates
#import certifi
#print(certifi.where())


import requests
import  pandas as pd
import numpy as np
from bs4 import BeautifulSoup

# Define url 
url = "https://contenido.bce.fin.ec/documentos/Estadisticas/SectorMonFin/MercadoInterbancario/IndiceMERINTER.htm"
# After, we read this "subpages"
#url = "https://contenido.bce.fin.ec/documentos/Estadisticas/SectorMonFin/MercadoInterbancario/mein0401.htm"


# Create empty lists
links_list = []
dates_list = []
dates_check_list = []
rates_list = []


# Scraping main page
# Recommended is:
#response = requests.get(url)
# With verify=False we are forcing
response = requests.get(url,verify=False)
html_content = response.content

# Extract all links, "subpages"
soup = BeautifulSoup(html_content, "html.parser")
links = soup.find_all("a")

# Filter
for link in links:
    # Convert to string the url
    link_text = str(link.get("href")) 
    # Assign to new list
    links_list.append(link_text)

# Filter
link_text = [x for x in links_list if "mailto" not in x]

# Keep date
for link in link_text:
    print("Link: ", link)
    # Extract date part
    part = link.split(".htm")[0][-4:]
    print("Date: ", part)
    # Append
    dates_list.append(part)

# Extract values
for link in link_text:   
# Read table and extract the value
        try:
            print("Link", link)
            # Load page and find table
            response = requests.get(link,verify=False)
            html_content = response.content

            soup = BeautifulSoup(html_content, "html.parser")
            tables = soup.find_all("table") 
            
            if len(tables) == 1:
                for table in tables:
                        try:
                            df = pd.read_html(str(table))[0]
                            #print(df)
                            # Keep the row of the monthly values
                            prome_mensual_row = df.loc[df[0] == "Prome.Mensual"]
                            #print(prome_mensual_row)
                            # Keep median
                            value = prome_mensual_row[2]
                        
                            value = value.values[0]
                            print("Value: ", value)
                            rates_list.append(value)
                            dates_check_list.append(link.split(".htm")[0][-4:])
                        except:
                            print("Error in: ", link)
                            rates_list.append(np.nan)
                            dates_check_list.append(link.split(".htm")[0][-4:])
                    
            else:  
                    print("Error in: ", link)
                    rates_list.append(np.nan)
                    dates_check_list.append(link.split(".htm")[0][-4:])
                    
        except:
            print("Error in: ", link)
            rates_list.append("Error")

# Format
rates_list2 = rates_list

for i in range(len(rates_list2)):
    if isinstance(rates_list2[i], str):
        if "." not in rates_list2[i]:
            rates_list2[i] = float(rates_list2[i]) / 10
        else:
            rates_list2[i] = float(rates_list2[i])
    elif np.isnan(rates_list2[i]):
        # Handle NaN values as needed
        pass
    else:
        # Handle other types if necessary
        pass
    
    
# Make DF
columns= ["Date", "Rate"]
df_rate = pd.DataFrame(columns = columns)
df_rate["Date"] = dates_list
df_rate["Rate"]  = rates_list2


# Convert the "Date" column to a proper datetime format
df_rate["Date"] = pd.to_datetime(df_rate["Date"], format='%m%y')

# Sort the DataFrame by the "Date" column
df_rate = df_rate.sort_values(by="Date")

# Reset the index after sorting
df_rate = df_rate.reset_index(drop=True)

# Filter rows based on conditions
# There are errors due to web format (, instead of .)
condition = (df_rate["Rate"] >= 10) & (df_rate["Date"].dt.year > 2006)
df_rate.loc[condition, "Rate"] /= 10

# Replace "Rate" with NaN for rows where the rate is 0 (blank in page)
df_rate.loc[df_rate["Rate"] == 0, "Rate"] = np.nan

# Display the sorted DataFrame
print(df_rate)

# Create a reference DataFrame with a complete sequence of months and years
min_date = df_rate["Date"].min()
max_date = df_rate["Date"].max()
date_range = pd.date_range(min_date, max_date, freq='MS')

reference_df = pd.DataFrame({"Date": date_range})

# Check for missing months
missing_months = reference_df[~reference_df["Date"].isin(df_rate["Date"])]

if not missing_months.empty:
    print("Missing months:")
    print(missing_months)
else:
    print("Data for all months is present.")

# Conclusion: there are missings months

# A new DataFrame (missing_data_df) is created with the missing months
# and NaN values for the "Rate" column
if not missing_months.empty:
    print("Missing months:")
    print(missing_months)

    # Create a new DataFrame with missing months and NaN values for the "Rate" column
    missing_data_df = pd.DataFrame({"Date": missing_months["Date"], "Rate": [None] * len(missing_months)})

    # Display the new DataFrame for manual completion
    print("Manually complete the missing data:")
    print(missing_data_df)

    # After manual completion, merge the new DataFrame with the original DataFrame
    df_rate = pd.concat([df_rate, missing_data_df], ignore_index=True)

    # Sort the DataFrame by the "Date" column
    df_rate = df_rate.sort_values(by="Date")

    # If you want to reset the index after sorting
    df_rate = df_rate.reset_index(drop=True)

    # Display the updated and sorted DataFrame
    print("Updated DataFrame:")
    print(df_rate)
else:
    print("Data for all months is present.")



# In[2]: Export
export_path = "C:\\Users\\Franco\\Documents\\0. Clases\\Macroeconometría 2023\\2023 TPs\\rate_bce.xlsx"
df_rate.to_excel(export_path, index=False)

# In[3]: Complete missings values
df_rate_merged = df_rate
df_rate_merged.loc[df_rate_merged["Date"].dt.strftime('%Y-%m') == '2006-01', "Rate"] = 2.13
df_rate_merged.loc[df_rate_merged["Date"].dt.strftime('%Y-%m') == '2006-03', "Rate"] = 2.3
df_rate_merged.loc[df_rate_merged["Date"].dt.strftime('%Y-%m') == '2006-06', "Rate"] = 2.42
df_rate_merged.loc[df_rate_merged["Date"].dt.strftime('%Y-%m') == '2006-09', "Rate"] = 2.66
df_rate_merged.loc[df_rate_merged["Date"].dt.strftime('%Y-%m') == '2008-12', "Rate"] = 0.5

# Sort the DataFrame by the "Date" column
df_rate_merged = df_rate_merged.sort_values(by="Date")

# If you want to reset the index after sorting
df_rate_merged = df_rate_merged.reset_index(drop=True)
# Format
df_rate_merged["Rate"] = pd.to_numeric(df_rate_merged["Rate"], errors='coerce')

# Delete duplicates based on all columns
df_rate_merged = df_rate_merged.drop_duplicates()

# Export
export_path_merged = "C:\\Users\\Franco\\Documents\\0. Clases\\Macroeconometría 2023\\2023 TPs\\rate_bce_missings.xlsx"
df_rate_merged.to_excel(export_path_merged, index=False)

