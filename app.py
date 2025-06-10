import streamlit as st
import pandas as pd
import json
import os
import sys

st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

def scan_tmp_for_datasets(tmp_dir="./tmp"):
    datasets = {}
    if not os.path.exists(tmp_dir):
        return datasets
    
    for folder in os.listdir(tmp_dir):
        folder_path = os.path.join(tmp_dir, folder)
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, f"{folder}_edited.csv")
            desc_path = os.path.join(folder_path, "descriptions.json")
            overture_path = os.path.join(folder_path, "overture_data.csv")
            summary_path = os.path.join(folder_path, "summary.txt")
            overture_dif_path = os.path.join(folder_path, "discrepancies_from_overture.csv")
            dataset_dif_path = os.path.join(folder_path, "discrepancies_from_other.csv")


            # Check if all files exist
            if os.path.exists(file_path) and os.path.exists(desc_path) and os.path.exists(overture_path):
                datasets[folder] = {
                    "file": file_path,
                    "description": desc_path,
                    "overture": overture_path,
                    "summary": summary_path,
                    "overture_dif_path": overture_dif_path,
                    "dataset_dif_path": dataset_dif_path
                }
    return datasets


# Initialize or update session state datasets on app start
if "uploaded_datasets" not in st.session_state:
    st.session_state.uploaded_datasets = scan_tmp_for_datasets()
else:
    # Optionally update to include any new folders discovered on rerun
    current_datasets = scan_tmp_for_datasets()
    for k, v in current_datasets.items():
        if k not in st.session_state.uploaded_datasets:
            st.session_state.uploaded_datasets[k] = v

# --- Sidebar ---
st.sidebar.title("Datasets")
st.sidebar.markdown("**Available Datasets**")

# Upload Section
st.sidebar.markdown("---")
with st.sidebar.expander("➕ Add Dataset"):
    uploaded_file = st.file_uploader("Upload a CSV", type=["csv"], key="uploader")
    dataset_name = st.text_input("Enter a name for the dataset", key="name_input")

    if st.button("✅ Done", key="done_button"):
        if uploaded_file and dataset_name:
            # Process and update session state
            from main import process_dataset
            process_dataset(uploaded_file, dataset_name)
            file_path = f"./tmp/{dataset_name}/{dataset_name}_edited.csv"
            desc_path = f"./tmp/{dataset_name}/descriptions.json"
            overture_path = f"./tmp/{dataset_name}/overture_data.csv"  
            summary_path = f"./tmp/{dataset_name}/summary.txt"
            overture_dif_path = f"./tmp/{dataset_name}/discrepancies_from_overture.csv"  
            dataset_dif_path = f"./tmp/{dataset_name}/discrepancies_from_other.txt"

            st.session_state.uploaded_datasets[dataset_name] = {
                "file": file_path,
                "description": desc_path,
                "overture": overture_path,
                "overture_dif_path": overture_dif_path,
                "dataset_dif_path": dataset_dif_path
            }

            # Trigger rerun so sidebar updates
            st.rerun()
        else:
            st.warning("Please upload a file and enter a name.")

# --- Get the selected dataset files dynamically

# Sidebar dataset selector
selected_dataset = st.sidebar.radio(
    "Select a dataset",
    options=list(st.session_state.uploaded_datasets.keys())
)


# st.write("selected_dataset is", selected_dataset)

#if selected_dataset in st.session_state.uploaded_datasets:
if selected_dataset:
    dataset_info = st.session_state.uploaded_datasets[selected_dataset]

    try:
        with open(dataset_info["description"], "r") as f:
            descriptions = json.load(f)
    except FileNotFoundError:
        descriptions = {}

    df_dataset = load_csv(dataset_info["file"])
    df_overture = load_csv(dataset_info["overture"])
    df_overture_diff = load_csv(dataset_info["overture_dif_path"])
    df_other_diff = load_csv(dataset_info["dataset_dif_path"])

else:
    descriptions = {}
    df_dataset = pd.DataFrame()
    df_overture = pd.DataFrame()
    df_overture_diff = pd.DataFrame()
    df_other_diff = pd.DataFrame()

n = dataset_info["file"]
#st.write("dataset_info['file']", n)
n = dataset_info["overture"]
#st.write("dataset_info['overture']", n)

# --- Main Page Layout ---

st.markdown(
    """
    <style>
        .summary-box {
            border: 1px solid #ccc;
            padding: 15px;
            margin-bottom: 20px;
            height: 20vh;
            overflow-y: auto;
            border-radius: 8px;
            background-color: #eef7ff;
        }
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

# -- Summary --
# Example: Load summary from file or variable

summary_text = ""
if "summary" in dataset_info and os.path.exists(dataset_info["summary"]):
    with open(dataset_info["summary"], "r") as f:
        summary_text = f.read()
else:
    summary_text = "No summary available for this dataset."

# Display summary
st.markdown(
    '<div class="summary-box"><strong>📊 Dataset Summary:</strong><br><br>{}</div>'.format(
        summary_text.replace("\n", "<br>")
    ),
    unsafe_allow_html=True
)

# --- Features Box ---

st.markdown("### Features Box")

if not df_dataset.empty:
    desc_row = [descriptions.get(col, "No description available.") for col in df_dataset.columns]
    features_data = pd.DataFrame([desc_row], columns=df_dataset.columns, index=["Description"])
    st.dataframe(features_data, use_container_width=True, height=150)
else:
    st.info("No dataset loaded yet. Please upload or select a dataset.")

st.markdown('</div>', unsafe_allow_html=True)


# --- Bottom Boxes (split view) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Overture Box")
    if not df_overture_diff.empty:
        st.dataframe(df_overture_diff, use_container_width=True, height=500)
    else:
        st.info("No overture data available.")

with col2:
    st.markdown("### Dataset Box")
    if not df_other_diff.empty:
        st.dataframe(df_other_diff, use_container_width=True, height=500)
    else:
        st.info("No dataset loaded yet.")


