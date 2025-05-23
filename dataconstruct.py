import pandas as pd
from fuzzywuzzy import fuzz


# Load the datasets
sbs_businesses = pd.read_csv('data/sbs_businesses.csv')
nyc_pois = pd.read_csv('data/nyc_pois.csv')
nyc_restaurants = pd.read_csv('data/nyc_restaurants.csv')

def normalize_name(name):
    """
    Normalize the name by converting to lowercase and stripping whitespace.
    """
    if pd.isnull(name):
        return ""
    return ''.join(e for e in name.lower() if e.isalnum() or e.isspace()).strip()

def normalize_address(building, street, zip_code):
    """
    Normalize the address by converting to lowercase and stripping whitespace.
    """
    parts = [str(building).strip(), str(street).strip(), str(zip_code).strip()]
    return ''.join(filter(None, parts)).lower()

# Normalize SBS Data
sbs_businesses['normalized_name'] = sbs_businesses['Vendor_DBA'].fillna(sbs_businesses['Vendor_Formal_Name']).apply(normalize_name)
sbs_businesses['normalized_address'] = sbs_businesses.apply(
    lambda row: normalize_address(row['Address_Line_1'], '', row['Postcode']), axis=1)

# Normalize Restaurant Data 
nyc_restaurants['normalized_name'] = nyc_restaurants['DBA'].apply(normalize_name)
nyc_restaurants['normalized_address'] = nyc_restaurants.apply(
    lambda row: normalize_address(row['BUILDING'], row['STREET'], row['ZIPCODE']), axis=1)

# Normalize POI Data 
nyc_pois['normalized_name'] = nyc_pois['FEATURE NAME'].apply(normalize_name)

# Check if data has been loaded correctly
print("SBS Sample:", sbs_businesses[['normalized_name', 'normalized_address']].head(3))
print("Restaurant Sample:", nyc_restaurants[['normalized_name', 'normalized_address']].head(3))
print("POI Sample:", nyc_pois[['normalized_name']].head(3))