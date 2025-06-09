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

    # Track min/max
    lat_vals = lat.tolist()
    lon_vals = lon.tolist()

    bounds = {
        "xmin": min(lon_vals),
        "xmax": max(lon_vals),
        "ymin": min(lat_vals),
        "ymax": max(lat_vals),
    }

    base, ext = os.path.splitext(file_path)
    edited_path = f"{base}_edited{ext}"
    df.to_csv(edited_path, index=False)
    return bounds

if __name__ == "__main__":
    bounds = rename_csv_file(file_path="./tmp/sample_nyc.csv")

    print(bounds)


