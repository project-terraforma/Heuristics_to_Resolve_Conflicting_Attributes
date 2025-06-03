!pip install overturemaps pandas geopandas shapely pyarrow folium matplotlib mapclassify
pd.set_option('display.max_colwidth', None)

import overturemaps
import geopandas as gpd
from shapely import wkb
import pandas as pd

# Define bounding box (Milan — same region as your earlier examples)
bbox = -4.0033, 0, -2.6033, 40.5167

# Get 'place' data within bbox — uses OvertureMaps core module
gdf = overturemaps.core.geodataframe("place", bbox=bbox)

# Preview columns and first rows
print(gdf.columns)
print(gdf.head())
print(len(gdf))

print("\ncategories", gdf['categories'][1])
print("\nsources", gdf['sources'][1])
print("\nbbox", gdf['bbox'][1])
print("\nnames", gdf['names'][1])
print("\naddresses", gdf['addresses'][1])

all_sources = gdf['sources'].dropna().explode()

# Extract 'dataset' values from each dictionary
all_datasets = all_sources.apply(lambda x: x.get('dataset') if isinstance(x, dict) else None)

# Drop missing values and get unique datasets
unique_datasets = pd.Series(all_datasets.dropna().tolist()).unique()

print(unique_datasets)


# Optional: Just get sample of 5 places
sample_gdf = gdf.sample(n=5, random_state=42)

print("hi \n")

# Plot sample points (optional)
print(sample_gdf.explore())

# Save locally if needed
sample_gdf.to_parquet("places-sample-region.parquet", index=False)

def get_source_confidence(sources_list):
    if isinstance(sources_list, list) and len(sources_list) > 0:
        return sources_list[0].get('confidence', None)
    return None

count = 0
for x in range(len(gdf)):
    source_conf = gdf['sources'][x][0]['confidence']
    top_conf = gdf['confidence'][x]
    if abs(source_conf - top_conf) < 1e-6:
        count += 1
    elif gdf['sources'][x][0]['confidence'] != 0.77:
      print(gdf.loc[x,:], "\n")
print(count)


