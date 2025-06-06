import pandas as pd
from fuzzywuzzy import fuzz
from tqdm import tqdm

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

load_datasets()
sbs_businesses = datasets["sbs_businesses"]
nyc_pois = datasets["nyc_pois"]
nyc_restaurants = datasets["nyc_restaurants"]

# Normalize Data
sbs_businesses['normalized_name'] = sbs_businesses['vendor_dba'].fillna(sbs_businesses['vendor_formal_name']).apply(normalize_name)
sbs_businesses['normalized_address'] = sbs_businesses.apply(
    lambda row: normalize_address(row['address1'], '', row['zip']), axis=1) 
nyc_restaurants['normalized_name'] = nyc_restaurants['dba'].apply(normalize_name)
nyc_restaurants['normalized_address'] = nyc_restaurants.apply(
    lambda row: normalize_address(row['building'], row['street'], row['zipcode']), axis=1)
nyc_pois['normalized_name'] = nyc_pois['FEATURE NAME'].apply(normalize_name)

sbs_index = sbs_businesses.groupby('normalized_address')
tqdm.pandas()

def match_restaurant_to_sbs(row):
    addr = row['normalized_address']
    name = row['normalized_name']
    
    if addr in sbs_index.groups:
        candidates = sbs_index.get_group(addr)
        best_match = None
        best_score = 0
        
        for _, sbs_row in candidates.iterrows():
            score = fuzz.token_set_ratio(name, sbs_row['normalized_name'])
            if score > best_score:
                best_score = score
                best_match = sbs_row
        
        if best_score >= 85:
            return pd.Series({
                "sbs_name": best_match['normalized_name'],
                "sbs_address": best_match['normalized_address'],
                "match_score": best_score,
                "sbs_index": best_match.name
            })
    
    return pd.Series({"sbs_name": None, "sbs_address": None, "match_score": 0, "sbs_index": None})

# Apply matching
matched_df = nyc_restaurants.copy()
matched_df[['sbs_name', 'sbs_address', 'match_score', 'sbs_index']] = matched_df.progress_apply(match_restaurant_to_sbs, axis=1)

# Filter to confident matches
final_matches = matched_df[matched_df['match_score'] >= 85]

poi_names = nyc_pois['normalized_name'].dropna().unique().tolist()

def best_poi_match(name):
    try:
        if not isinstance(name, str) or not name.strip():
            return pd.Series([None, 0], index=["poi_name", "poi_score"])

        best_score = 0
        best_name = None
        for poi in poi_names:
            score = fuzz.token_set_ratio(name, poi)
            if score > best_score:
                best_score = score
                best_name = poi

        return pd.Series([best_name, best_score], index=["poi_name", "poi_score"])
    except Exception as e:
        print(f"Error matching POI for name: {name}, Error: {e}")
        return pd.Series([None, 0], index=["poi_name", "poi_score"])



final_matches[['poi_name', 'poi_score']] = final_matches['normalized_name'].progress_apply(best_poi_match)
final_matches.to_csv("merged_confident_matches.csv", index=False)

