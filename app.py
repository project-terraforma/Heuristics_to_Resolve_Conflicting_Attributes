import streamlit as st
import pandas as pd
import json
import os

# Load data
@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

st.set_page_config(layout="wide")

# Paths
dataset_path = "./tmp/sample_nyc/sample_nyc_edited.csv"
descriptions_path = "./tmp/sample_nyc/descriptions.json"
overture_path = "./tmp/sample_nyc/overture_data.csv"

# Load core datasets
df_dataset = load_csv(dataset_path)
df_overture = load_csv(overture_path)
with open(descriptions_path, "r") as f:
    descriptions = json.load(f)

# --- Sidebar ---
st.sidebar.title("Datasets")

# Store uploaded datasets and form state in session
if "uploaded_datasets" not in st.session_state:
    st.session_state.uploaded_datasets = {}
if "show_upload_form" not in st.session_state:
    st.session_state.show_upload_form = False

# Show available datasets
available_datasets = ["nyc_restaurants.csv"] + list(st.session_state.uploaded_datasets.keys())
selected_dataset = st.sidebar.radio("Select a dataset", options=available_datasets)

# Show/hide upload popup
if st.sidebar.button("➕ Add Dataset"):
    st.session_state.show_upload_form = True

if st.session_state.show_upload_form:
    with st.sidebar.expander("Upload New Dataset", expanded=True):
        uploaded_file = st.file_uploader("Upload CSV", type="csv", key="file")
        dataset_name = st.text_input("Dataset Name", key="name")

        if uploaded_file and dataset_name:
            save_path = f"./tmp/uploads/{dataset_name}.csv"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Save the dataset reference
            st.session_state.uploaded_datasets[dataset_name] = save_path

            from main import process_dataset
            process_dataset(save_path, dataset_name)

        # ✅ Call rerun only on click
        if st.button("Done"):
            st.session_state.show_upload_form = False
            st.rerun()




# --- Main Page Layout ---

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

# Description row
desc_row = [descriptions.get(col, "Description") for col in df_dataset.columns]
features_data = pd.DataFrame([desc_row], columns=df_dataset.columns, index=["Description"])
st.dataframe(features_data, use_container_width=True, height=150)
st.markdown('</div>', unsafe_allow_html=True)

# --- Bottom Boxes (split view) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Overture Box")
    st.dataframe(df_overture.head(50), use_container_width=True, height=500)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### Dataset Box")

    # Load selected dataset (if dynamic)
    if selected_dataset in st.session_state.uploaded_datasets:
        dynamic_path = st.session_state.uploaded_datasets[selected_dataset]
        df_dynamic = load_csv(dynamic_path)
        st.dataframe(df_dynamic.head(50), use_container_width=True, height=500)
    else:
        st.dataframe(df_dataset.head(50), use_container_width=True, height=500)

    st.markdown('</div>', unsafe_allow_html=True)
