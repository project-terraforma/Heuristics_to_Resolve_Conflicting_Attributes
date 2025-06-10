# Detailed Documentation: Heuristics to Resolve Conflicting Attributes

This document provides in-depth descriptions of all Python modules in the repository, including functions and docstrings.

## `analyze.py`

**Module Description:** _No module-level docstring._

### Function: `get_descriptions`
- **Arguments:** df, name
- **Description:** No docstring provided.

### Function: `get_col_names`
- **Arguments:** df
- **Description:** No docstring provided.

## `app.py`

**Module Description:** _No module-level docstring._

### Function: `load_csv`
- **Arguments:** path
- **Description:** No docstring provided.

### Function: `scan_tmp_for_datasets`
- **Arguments:** tmp_dir
- **Description:** No docstring provided.

## `compare.py`

**Module Description:** _No module-level docstring._

### Function: `llm_verify_name_match`
- **Arguments:** overture_name, other_name
- **Description:** Ask LLM if two names refer to the same place.

### Function: `parse_address1`
- **Arguments:** address
- **Description:** Extract number and lowercase street name from a freeform address.

### Function: `compare_n`
- **Arguments:** overture_dataset_path, other_dataset_path
- **Description:** No docstring provided.

### Function: `recheck_other_discrepancies`
- **Arguments:** overture_df, other_discrepancy_rows
- **Description:** No docstring provided.

## `get_overture_data.py`

**Module Description:** _No module-level docstring._

### Function: `get_overture_data`
- **Arguments:** bbox, file_path
- **Description:** Fetch data within the specified bounding box using overture,
convert to pandas DataFrame, and save as tmp/overture_data.csv.

Parameters:
- bbox: tuple of floats (minx, miny, maxx, maxy)

## `main.py`

**Module Description:** _No module-level docstring._

### Function: `process_dataset`
- **Arguments:** file_obj, dataset_name
- **Description:** No docstring provided.

## `analyze_dataset.py`

**Module Description:** _No module-level docstring._

### Function: `make_standard_cols`
- **Arguments:** df, dataset_name, num, name_col, address_col, lat_lon
- **Description:** No docstring provided.

