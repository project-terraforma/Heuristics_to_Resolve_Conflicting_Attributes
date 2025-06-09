# 🧪 Initial Exploration: Overture Maps Data

This document outlines the first steps in using the `overturemaps` Python package to retrieve, explore, and analyze place data within a geographic bounding box.

---

## 📦 Dependencies

Install required packages (if not already installed):

```bash
pip install overturemaps pandas geopandas shapely pyarrow folium matplotlib mapclassify
```

Set pandas options to show full text in columns:

```python
import pandas as pd
pd.set_option('display.max_colwidth', None)
```

---

## 🌍 Define Bounding Box

A bounding box (`bbox`) is defined to extract geographic data. In this example, the coordinates are set for a region near Milan (but seem to be off — may need correction):

```python
bbox = (-4.0033, 0, -2.6033, 40.5167)
```

---

## 🗂️ Load Place Data

Using the OvertureMaps package:

```python
import overturemaps
gdf = overturemaps.core.geodataframe("place", bbox=bbox)
```

This returns a **GeoPandas DataFrame** with place data in the region.

---

## 🔍 Inspect Data

Basic preview of the dataset:

```python
print(gdf.columns)
print(gdf.head())
print(len(gdf))
```

Inspect common fields such as:

- `categories`
- `sources`
- `bbox`
- `names`
- `addresses`

---

## 🧬 Source Dataset Analysis

Extract and list all unique data sources:

```python
all_sources = gdf['sources'].dropna().explode()
all_datasets = all_sources.apply(lambda x: x.get('dataset') if isinstance(x, dict) else None)
unique_datasets = pd.Series(all_datasets.dropna().tolist()).unique()
print(unique_datasets)
```

---

## 🗺️ Visualize and Save Sample

Take a random sample of 5 places and visualize them:

```python
sample_gdf = gdf.sample(n=5, random_state=42)
sample_gdf.explore()
sample_gdf.to_parquet("places-sample-region.parquet", index=False)
```

---

## 🧠 Confidence Matching

Compare top-level confidence score with the confidence from the first source entry for each place:

```python
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
```

This helps verify the alignment between the source-level confidence and the top-level confidence.

---

## ✅ Summary

This notebook sets the foundation for:
- Bounding box querying
- Source dataset validation
- Confidence consistency checks
- Sample visualization and export

