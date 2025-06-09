import os, json, pandas as pd
from dotenv import load_dotenv
import dspy
from dspy import InputField, OutputField, Signature, Predict

# ---------- LLM setup ----------
load_dotenv()
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
lm = dspy.LM("openai/gpt-3.5-turbo", api_key=OPEN_AI_KEY)
dspy.configure(lm=lm)

# ---------- DSPy Signatures ----------
class FieldMappingSignature(Signature):
    """Map the user’s dataset columns to standardized fields."""
    columns: list[str]          = InputField(desc="List of column names")
    sample_rows: list[dict]     = InputField(desc="Up to ten example rows")
    field_mapping: str          = OutputField(desc=(
        "Python dict mapping {'name','latitude','longitude','address'} → best-matching column(s).\n"
        "For ‘address’ return a list ordered [addr#, street, zipcode, city, state, country] "
        "(omit items you can’t find). For combined lat/lon columns use "
        "[column_name, 0] (lat,lon) or [column_name, 1] (lon,lat). "
        "Use 'N/A' only when no sensible match exists."))

class DatasetSummarySignature(Signature):
    """Write a concise, one-sentence overview of the dataset’s purpose."""
    columns: list[str]          = InputField(desc="List of column names")
    sample_rows: list[dict]     = InputField(desc="Up to ten example rows")
    summary: str                = OutputField(desc="Short summary (<= 30 words)")

class ColumnDescriptionsSignature(Signature):
    """Give a terse description for each column."""
    columns: list[str]          = InputField(desc="List of column names")
    descriptions: str           = OutputField(desc=(
        "Python list of 1-sentence descriptions, same order as input. "
        "Format: ['<col>: <description>', …]"))

# ---------- Predict modules ----------
field_mapper      = Predict(FieldMappingSignature)
summarizer        = Predict(DatasetSummarySignature)
column_describer  = Predict(ColumnDescriptionsSignature)

# ---------- Helper functions ----------
def get_descriptions(df: pd.DataFrame, name: str) -> None:
    columns      = df.columns.tolist()
    sample_rows  = df.head(10).to_dict(orient="records")

    # 1️⃣ Dataset summary
    summary      = summarizer(columns=columns, sample_rows=sample_rows).summary

    # 2️⃣ Column descriptions
    col_resp     = column_describer(columns=columns).descriptions
    try:
        col_desc = eval(col_resp)           # convert returned string → list
    except Exception:
        col_desc = ["Description not available"] * len(columns)

    # 3️⃣ Persist to tmp/<name>/
    folder = os.path.join("tmp", name)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "descriptions.json"), "w") as f:
        json.dump(dict(zip(columns, col_desc)), f, indent=4)
    with open(os.path.join(folder, "summary.txt"), "w") as f:
        f.write(summary)

def get_col_names(df: pd.DataFrame):
    columns     = df.columns.tolist()
    sample_rows = df.head(10).to_dict(orient="records")

    resp = field_mapper(columns=columns, sample_rows=sample_rows).field_mapping
    mapping = eval(resp)

    name_col = mapping.get("name", "N/A")
    lat_col  = mapping.get("latitude", "N/A")
    lon_col  = mapping.get("longitude", "N/A")
    addr_col = mapping.get("address", "N/A")

    print(mapping)              # 👀 inspect raw mapping
    print([lat_col, lon_col])   # 👀 lat / lon check
    return name_col, [lat_col, lon_col], addr_col

# ---------- Example ----------
if __name__ == "__main__":
    df = pd.read_csv("./tmp/lat_lon.csv")   # or any DataFrame
    result = get_col_names(df)
    print("\n🔎 Final Output Tuple:")
    print(result)
