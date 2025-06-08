### NOT DONE GETTING ERRORS

import pandas as pd
from fuzzywuzzy import fuzz


# Load the datasets
datasets = {
    "sbs_businesses": "https://data.cityofnewyork.us/resource/ci93-uc8s.csv",
    "nyc_pois": "https://data.cityofnewyork.us/api/views/t95h-5fsr/rows.csv?date=20250523&accessType=DOWNLOAD",
    "nyc_restaurants": "https://data.cityofnewyork.us/resource/43nn-pn8j.csv"
}

def load_datasets():
    """
    Load datasets from the provided URLs.
    """
    for name, url in datasets.items():
        try:
            datasets[name] = pd.read_csv(url)
            print(f"Loaded {name} with {len(datasets[name])} rows.")
        except Exception as e:
            print(f"Failed to load {name}: {e}")

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

# Load datasets
load_datasets()
# Extract datasets
sbs_businesses = datasets["sbs_businesses"]
nyc_pois = datasets["nyc_pois"]
nyc_restaurants = datasets["nyc_restaurants"]

# Normalize SBS Data
sbs_businesses['normalized_name'] = sbs_businesses['vendor_dba'].fillna(sbs_businesses['vendor_formal_name']).apply(normalize_name)
sbs_businesses['normalized_address'] = sbs_businesses.apply(
    lambda row: normalize_address(row['address1'], '', row['zip']), axis=1)

# Normalize Restaurant Data 
nyc_restaurants['normalized_name'] = nyc_restaurants['dba'].apply(normalize_name)
nyc_restaurants['normalized_address'] = nyc_restaurants.apply(
    lambda row: normalize_address(row['building'], row['street'], row['zipcode']), axis=1)

# Normalize POI Data 
nyc_pois['normalized_name'] = nyc_pois['FEATURE NAME'].apply(normalize_name)

# Check if data has been loaded correctly
print("SBS Sample:", sbs_businesses[['normalized_name', 'normalized_address']].head(3))
print("Restaurant Sample:", nyc_restaurants[['normalized_name', 'normalized_address']].head(3))
print("POI Sample:", nyc_pois[['normalized_name']].head(3))