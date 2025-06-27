# 🗺️ Overture Dataset Comparison Tool

This tool helps identify discrepancies between [Overture Maps](https://overturemaps.org/) data and external datasets. It uses AI/LLM assistance to validate schema compatibility and provides an interactive UI for exploring mismatches, all within a specified bounding box (bbox). 

[Link to Demo](https://drive.google.com/file/d/1MbpsiKyx2UnziMIcNHaDtpLSpyBxGaM1/view?usp=sharing)
---

## 📁 Project Structure

### `app.py`
- **Description:** Streamlit frontend
- **Function:** Allows dataset uploads, triggers comparison logic, and displays results interactively

### `get_overture_data.py`
- **Input:** Bounding box (`minlon`, `maxlon`, `minlat`, `maxlat`)
- **Function:** Fetches Overture data for the given bbox
- **Output:** Saves Overture data as a **Pandas DataFrame** (no geometry) to `/tmp/`

### `analyze_dataset.py`
- **Input:** Path to a CSV dataset
- **Function:**
  - Uses an LLM to detect key columns: business name, lat/lon, and address
  - Rejects datasets lacking these columns
  - Generates short AI-powered descriptions for each column
- **Output:**
  ```python
  {
    "column_descriptions": {...},
    "business_name_col": "name",
    "lat_col": "latitude",
    "lon_col": "longitude",
    "address_col": "address"
  }
  ```

### `compare.py`
- **Input:** Overture dataset + user-provided dataset
- **Function:**
  - Compares records between the two datasets
  - Uses bbox containment instead of precise lat/lon geometry
  - Identifies and logs rows with mismatched or missing data
- **Output:**
  ```python
  {
    "overture_discrepency_rows": [...],
    "other_dataset_discrepency_rows": [...]
  }
  ```

---

## ⚙️ How It Works

1. Upload a dataset via the Streamlit UI.
2. Dataset is saved to `/tmp/`.
3. `analyze_dataset.py` uses LLM to identify key columns.
4. `get_overture_data.py` fetches Overture data within the appropriate bounding box.
5. `compare.py` checks for discrepancies and prepares a summary.
6. Mismatches are displayed through the Streamlit dashboard.

---

## 📝 Notes

- **No geometry used:** We avoid exporting Overture data as a GeoPandas `GeoDataFrame`. Instead, we use bounding box coordinates (`minlon`, `maxlon`, `minlat`, `maxlat`).
- **Streamlit saves files in `/tmp/`** for temporary use.
- **LLM-assisted schema detection** makes the tool flexible across diverse dataset formats.

---

## 🚀 Getting Started (Optional Section)

> Coming soon: setup instructions and environment requirements.

---

## 📜 License

Apache 2.0

---

## Bugs
--- 
Compare.py can be improved in comparing addresses. Right now, some addresses that are different but similar are treated as the same. The names for these entities are compared, which should not happen. Ex: "45 W 21st St" and "45 W 132nd Street Apt 16N New York NY 10037" are considered to be the same address. Address parsing could also be improved to parse the address zip code, city, state, and country. 

## Future Work
--- 
* Make a more robust analyzing process that can extract desired column names for a larger variety of datasets.
* Add another check (web-scraping) to decide if a name change should be made.
* Output a file with the rows with discrepancies. This file should be in the format of Overture's data but have the name changed. This is so that a human reviewer can easily commit these changes 
* Reject a dataset if it does not contain address, name, and lat/lon data.
* Add a loading screen on streamlit.
