import os
import pandas as pd
from dotenv import load_dotenv

import dspy
from dspy import InputField, OutputField, Signature, Predict

# === Load OpenAI Key and Configure LLM ===
load_dotenv()
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")

lm = dspy.LM("openai/gpt-3.5-turbo", api_key=OPEN_AI_KEY)
dspy.configure(lm=lm)

# === DSPy Signatures ===

class FieldMappingSignature(Signature):
    columns: str = InputField(desc="List of column names from a dataset")
    field_mapping: str = OutputField(desc=(
        "Python dict mapping {'name', 'latitude', 'longitude', 'address'} to their best-matching column names. "
        "Use 'N/A' only if no close match exists."
    ))

class DatasetSummarySignature(Signature):
    context: str = InputField(desc="Dataset preview: columns + sample rows")
    summary: str = OutputField(desc="Short summary of what the dataset is and why it's useful")

class ColumnDescriptionsSignature(Signature):
    column_list: str = InputField(desc="List of column names from a dataset")
    descriptions: str = OutputField(desc=(
        "Python list of short descriptions (1 sentence or less) for each column, "
        "in the same order as the input. Format: "
        "['<col1>: <description>', '<col2>: <description>', ...]"
    ))

# === DSPy Predict Modules ===
field_mapper = Predict(FieldMappingSignature)
summarizer = Predict(DatasetSummarySignature)
column_describer = Predict(ColumnDescriptionsSignature)

# === Main Analyzer Function ===

def analyze_location_dataset(csv_path: str):
    df = pd.read_csv(csv_path)
    columns = list(df.columns)
    sample_rows = df.head(3).to_dict(orient="records")

    # Run field mapping
    field_response = field_mapper(columns=str(columns))
    field_mapping = eval(field_response.field_mapping)

    # Extract fields if present
    name_col = field_mapping.get("name", "N/A")
    lat_col = field_mapping.get("latitude", "N/A")
    lon_col = field_mapping.get("longitude", "N/A")
    addr_col = field_mapping.get("address", "N/A")

    # Check if lat/lon are in same column
    lat_lon_same_field = lat_col == lon_col and lat_col != "N/A"

    # Run dataset summary
    summary_response = summarizer(context=f"Columns: {columns}\nSample: {sample_rows}")
    summary = summary_response.summary

    # Run column description
    col_desc_response = column_describer(column_list=str(columns))
    try:
        column_descriptions = eval(col_desc_response.descriptions)
    except:
        column_descriptions = ["Description not available"] * len(columns)

    return (name_col, lon_col, lat_col, lat_lon_same_field, addr_col, summary, column_descriptions)

# === Example Usage ===
if __name__ == "__main__":
    result = analyze_location_dataset("local_data/nyc_restaurants.csv")
    print("\n🔎 Final Output Tuple:")
    print(result)

    result = analyze_location_dataset("local_data/sf_data.csv")
    print("\n🔎 Final Output Tuple:")
    print(result)
