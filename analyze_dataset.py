# Take file path to dataset as input
# Make a new temp file that includes the first 70 lines of the dataset

# Prompt a small LLM to find the cols and get a short description of this

# Export this as a dictionary (print it but also return it)
# with the 
import pandas as pd
import os

## TO DO

## Fow now: default names of database cols

# Parameters
#if lat_lon is combined lat_lon paramter will be [col_name, 0] if it is in format lat, lon 
#                                                [col_name, 1] if it is in format lon, lat 
#if they are different cols, lat will come first

# address_col will either be one col or a few. 
# If it is a few the cols will be in order of a proper address: 

def rename_csv_file(file_path, name_col='dba', address_col=['building', 'street', 'zipcode'], lat_lon=['latitude', 'longitude']):
    df = pd.read_csv(file_path)

    # Rename name_col to unique_name
    df['unique_name'] = df[name_col]

    # Combine address columns into one string column if multiple provided
    if len(address_col) > 1:
        df['unique_address'] = df[address_col].astype(str).agg(' '.join, axis=1)
    elif len(address_col) == 1:
        df['unique_address'] = df[address_col[0]]
    else:
        raise ValueError("address_col must have at least one column name.")

    # Process lat/lon and build unique_lon_lat as dict {x: lon, y: lat}
    lat_vals = []
    lon_vals = []

    if len(lat_lon) == 2 and isinstance(lat_lon[0], list):
        # lat_lon is in format [[combined_col_name, order]]
        combined_col, order = lat_lon[0]
        split_coords = df[combined_col].astype(str).str.split(",", expand=True)
        if order == 0:  # lat, lon
            lat = split_coords[0].astype(float)
            lon = split_coords[1].astype(float)
        elif order == 1:  # lon, lat
            lon = split_coords[0].astype(float)
            lat = split_coords[1].astype(float)
        else:
            raise ValueError("lat_lon order must be 0 (lat, lon) or 1 (lon, lat)")
    elif len(lat_lon) == 2:
        # Separate lat and lon columns provided
        lat = df[lat_lon[0]].astype(float)
        lon = df[lat_lon[1]].astype(float)
    else:
        raise ValueError("lat_lon must be a list of two separate columns or a list of one [col_name, order].")

    df['unique_lon_lat'] = [{"x": x, "y": y} for x, y in zip(lon, lat)]

    # Filter out invalid lat/lon: non-numeric, NaN, or (0, 0)
    valid_mask = (~lat.isna()) & (~lon.isna()) & ~((lat == 0) & (lon == 0))
    lat_valid = lat[valid_mask]
    lon_valid = lon[valid_mask]

    df.loc[valid_mask, 'unique_lon_lat'] = [{"x": x, "y": y} for x, y in zip(lon_valid, lat_valid)]
    df.loc[~valid_mask, 'unique_lon_lat'] = None  # Set invalid ones to None

    # Calculate bounding box only for valid coordinates
    bounds = {
        "xmin": lon_valid.min(),
        "xmax": lon_valid.max(),
        "ymin": lat_valid.min(),
        "ymax": lat_valid.max(),
    }

    base, ext = os.path.splitext(file_path)
    edited_path = f"{base}_edited{ext}"
    df.to_csv(edited_path, index=False)
    return bounds

if __name__ == "__main__":
    descriptions = {
   "camis": "Unique identifier for each restaurant/food establishment in the system",
   "dba": "Doing Business As name; the operating name of the restaurant or food establishment",
   "boro": "Borough where the establishment is located (Manhattan, Brooklyn, Queens, Bronx, Staten Island)",
   "building": "Street number/building address",
   "street": "Street name where the establishment is located",
   "zipcode": "ZIP code of the establishment's location",
   "phone": "Contact phone number for the establishment",
   "cuisine_description": "Type of cuisine served (e.g., American, Chinese, Pizza, Thai)",
   "inspection_date": "Date when the health inspection was conducted",
   "action": "Result/action taken during inspection (e.g., 'Violations were cited', 'No violations recorded')",
   "violation_code": "Specific code identifying the type of health violation found",
   "violation_description": "Detailed description of the health violation",
   "critical_flag": "Indicates whether the violation is considered 'Critical' or 'Not Critical'",
   "score": "Numerical inspection score (higher scores indicate more violations)",
   "grade": "Letter grade assigned based on inspection (A, B, C, etc.)",
   "grade_date": "Date when the grade was assigned",
   "record_date": "Date when this record was entered into the system",
   "inspection_type": "Type of inspection conducted (e.g., 'Cycle Inspection', 'Pre-permit')",
   "latitude": "Geographic latitude coordinate of the establishment",
   "longitude": "Geographic longitude coordinate of the establishment",
   "community_board": "NYC community board district number",
   "council_district": "NYC council district number",
   "census_tract": "Census tract identifier",
   "bin": "Building Identification Number",
   "bbl": "Borough, Block, and Lot identifier",
   "nta": "Neighborhood Tabulation Area code",
   "location_point1": "Additional location reference point"
    }
    
    bounds = rename_csv_file(file_path="./tmp/sample_nyc.csv")

    print(bounds)


