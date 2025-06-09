import streamlit as st
import pandas as pd
import json

# Load data
@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

st.set_page_config(layout="wide")

dataset_path = "./tmp/sample_nyc/sample_nyc_edited.csv"
descriptions_path = "./tmp/sample_nyc/descriptions.json"
overture_path = "./tmp/sample_nyc/overture_data.csv"

df_dataset = load_csv(dataset_path)
df_overture = load_csv(overture_path)
with open(descriptions_path, "r") as f:
    descriptions = json.load(f)

# --- Sidebar ---
st.sidebar.title("Datasets")
st.sidebar.markdown("**Available Datasets**")
st.sidebar.radio("Select a dataset", options=["nyc_restaurants.csv"])

# Plus button at bottom
st.sidebar.markdown("---")
if st.sidebar.button("➕ Add Dataset"):
    st.sidebar.success("Feature not implemented yet!")

# --- Main Page Layout ---

# Set overall layout style
st.markdown(
    """
    <style>
        .features-box {
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 20px;
            height: 33vh;
            overflow-y: auto;
            border-radius: 8px;
            background-color: #f9f9f9;
        }
        .data-box {
            border: 1px solid #ccc;
            padding: 10px;
            height: 58vh;
            overflow-y: auto;
            border-radius: 8px;
            background-color: #fff;
        }
        .column-header {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .desc-text {
            font-style: italic;
            color: #666;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Features Box ---
st.markdown("### Features Box")

# Create a list of descriptions for each column, defaulting to "Description" if not found
desc_row = [descriptions.get(col, "Description") for col in df_dataset.columns]

# Create the features_data DataFrame
features_data = pd.DataFrame([desc_row], columns=df_dataset.columns, index=["Description"])

# Wrap it in a styled box
# st.markdown('<div class="features-box">', unsafe_allow_html=True)
st.dataframe(features_data, use_container_width=True, height=150)
st.markdown('</div>', unsafe_allow_html=True)

# --- Bottom Boxes (split view) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Overture Box")
    #st.markdown('<div class="data-box">', unsafe_allow_html=True)
    st.dataframe(df_overture.head(50), use_container_width=True, height=500)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### Dataset Box")
    #st.markdown('<div class="data-box">', unsafe_allow_html=True)
    st.dataframe(df_dataset.head(50), use_container_width=True, height=500)
    st.markdown('</div>', unsafe_allow_html=True)

