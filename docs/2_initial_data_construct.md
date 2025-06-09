# 🚀 Next Steps: Matching and Comparing Datasets

This document outlines the intermediate steps in the project: identifying name columns, preparing data for comparison, and running a robust DuckDB-based comparison between city datasets and Overture Maps.

---

## 🔍 Step 1: Identifying Place Name Columns (`find_name_col.py`)

### Purpose
Automatically identify the most likely column in a dataset that represents a **place or business name**.

### Key Features
- Uses `spaCy` Named Entity Recognition (NER) to score values as potential place names.
- Applies heuristics:
  - Column name keyword match
  - Capitalization and formatting
  - Entity labels like `ORG` or `FAC`
  - Filters out mostly numeric or overly verbose columns

### Usage
```python
df = pd.read_csv("https://data.cityofnewyork.us/resource/43nn-pn8j.csv")
best_col = find_place_name_column(df)
print(best_col)
```

---

## 🛠️ Step 2: Normalizing and Matching Data (`data_construct.py`)

### Purpose
Normalize and match entries across three NYC datasets:
- SBS Business Directory
- NYC Restaurants
- NYC Points of Interest (POIs)

### Techniques Used
- **Normalization**: Convert names/addresses to lowercase, remove punctuation.
- **Matching**:
  - Match restaurant records to SBS businesses by normalized address and fuzzy string similarity (via `fuzzywuzzy`)
  - Match restaurant names to POI names based on token set ratio

### Output
Creates `merged_confident_matches.csv` containing:
- Matched SBS business info
- POI match names and similarity scores

---

## 🧮 Step 3: Comparing with Overture Maps (`compare.py`)

### Purpose
Compare city-level datasets (e.g., DataSF business registry) with **Overture Maps – Places** data using **DuckDB**.

### Advantages
- Fully in-memory processing with DuckDB
- Minimal dependencies (just `duckdb`, `requests`)
- No guesswork on column names — uses explicit SOQL query
- S3 Parquet reader for Overture data

### How It Works
1. Downloads a trimmed dataset from DataSF via SoQL
2. Loads both datasets into DuckDB
3. Clips Overture data to bounding box
4. Performs spatial join + edit distance comparison
5. Filters mismatches based on name difference

### Run Instructions
```bash
pip install --upgrade duckdb
python compare.py --bbox "-122.52,37.70,-122.35,37.83" --distance 10 --outfile sf_mismatch.parquet
```

### Output
Parquet file containing mismatches with:
- `location_id`, `sf_name`
- `ovt_id`, `ovt_name`
- `dist_m`, `edit_dist`

---

## ✅ Summary

| Step | Purpose |
|------|---------|
| `find_name_col.py` | Identify business name column heuristically |
| `data_construct.py` | Normalize and match across NYC datasets |
| `compare.py` | Spatial and text comparison between city and Overture data |

