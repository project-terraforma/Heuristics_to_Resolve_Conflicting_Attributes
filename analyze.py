import os
import pandas as pd
import json
from dotenv import load_dotenv

import dspy
from dspy import InputField, OutputField, Signature, Predict

# === Load OpenAI Key and Configure LLM ===
load_dotenv()
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")

lm = dspy.LM("openai/gpt-3.5-turbo", api_key=OPEN_AI_KEY)
dspy.configure(lm=lm)

# === DSPy Signatures ===

# We could do a check to implement if lat or lon is first 
class FieldMappingSignature(Signature):
    context: str = InputField(desc="Dataset preview: columns + sample rows")
    field_mapping: str = OutputField(desc=(
        "Python dict mapping {'name', 'latitude', 'longitude', 'address'} to their best-matching column names. "
        "Address may have more than one col. If so, return a list of columns that includes at minimum address number and street name, "
        "and at most address number, street name, zipcode, city, state, country in that order. "
        "return the address as a list even if the list has only one entry."
        "For combined latitude/longitude columns, Indicate format as [column_name, 0] for (lat, lon) or [column_name, 1] for (lon, lat)."
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
def get_descriptions(df, name):
    columns = list(df.columns)
    sample_rows = df.head(10).to_dict(orient="records")

     # Run dataset summary
    summary_response = summarizer(context=f"Columns: {columns}\nSample: {sample_rows}")
    summary = summary_response.summary

    # Run column description
    col_desc_response = column_describer(column_list=str(columns))
    try:
        column_descriptions = eval(col_desc_response.descriptions)
    except:
        column_descriptions = ["Description not available"] * len(columns)
    
    # Prepare directory path
    folder_path = os.path.join("tmp", name)
    os.makedirs(folder_path, exist_ok=True)

    # Write column descriptions to tmp/name/descriptions.json
    desc_path = os.path.join(folder_path, "descriptions.json")
    with open(desc_path, "w") as f:
        json.dump(dict(zip(columns, column_descriptions)), f, indent=4)

    # Write general summary to tmp/name/summary.txt
    summary_path = os.path.join(folder_path, "summary.txt")
    with open(summary_path, "w") as f:
        f.write(summary)
    
    return

def get_col_names(df):
    #df = pd.read_csv(inp)
    columns = list(df.columns)
    sample_rows = df.head(10).to_dict(orient="records")

    # Run field mapping
    field_response = field_mapper(context=f"Columns: {columns}\nSample: {sample_rows}")
    field_mapping = eval(field_response.field_mapping)

    # Extract fields if present
    name_col = field_mapping.get("name", "N/A")
    lat_col = field_mapping.get("latitude", "N/A")
    lon_col = field_mapping.get("longitude", "N/A")
    addr_col = field_mapping.get("address", "N/A")

    print(field_mapping)
    print([lat_col, lon_col])
    
    return (name_col, [lat_col, lon_col], addr_col)

# === Example Usage ===
if __name__ == "__main__":
    result = get_col_names("./tmp/lat_lon.csv")
    print("\n🔎 Final Output Tuple:")
    print(result)

