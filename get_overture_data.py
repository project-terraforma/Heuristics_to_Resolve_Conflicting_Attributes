# Takes bbox as input.
# Uses overture to get data within specified bbox

# get that data as a pandas df
# save that df as a csv file in tmp/overture_data.csv 
# this file already exists you need to overwrite it. 

import os
import pandas as pd
import overturemaps

def get_overture_data(bbox, file_path):
    """
    Fetch data within the specified bounding box using overture,
    convert to pandas DataFrame, and save as tmp/overture_data.csv.

    Parameters:
    - bbox: tuple of floats (minx, miny, maxx, maxy)
    """
    print("entered function\n")

    # Get data as GeoDataFrame (example: 'place' data)
    gdf = overturemaps.core.geodataframe("place", bbox=bbox)
    print("saved data to gdf\n")

    # Convert to pandas DataFrame
    df = pd.DataFrame(gdf.drop(columns='geometry'))
    print("saved data to df from gdf\n")

    # Ensure tmp directory exists
    os.makedirs("tmp", exist_ok=True)
    print("checked that folder exists\n")

    # Save DataFrame to CSV, overwriting existing file
    csv_path = f"{file_path}/overture_data.csv"
    df.to_csv(csv_path, index=False)
    print("saved data to file\n")

    print(f"Overture data saved to {csv_path}")

# if __name__ == "__main__":
#     # Example bbox (replace with your bbox input)
#     bbox = (-4.0033, 0, -2.6033, 40.5167)
#     print("calling function\n")
#     get_overture_data(bbox)

