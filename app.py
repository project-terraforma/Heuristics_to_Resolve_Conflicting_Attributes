import streamlit as st
import pandas as pd
import geopandas as gpd

# -----------------------------
# Load datasets
# -----------------------------
@st.cache_data
def load_datasets():
    overture_data = gpd.read_file("overture_data.geojson")
    other_data = pd.read_csv("nyc_restaurants.csv")
    return overture_data, other_data

overture_df, other_df = load_datasets()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Datasets")
datasets = ["nyc_restaurants.csv", "overture_data.geojson"]

# Display without bullet points using markdown and no unordered list markers
for dataset in datasets:
    st.sidebar.markdown(f"{dataset}", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.button("➕ Add Dataset")

# -----------------------------
# Main Layout
# -----------------------------
st.markdown(
    """
    <style>
        .container-box {
            border: 1px solid #CCC;
            padding: 16px;
            margin-bottom: 16px;
            border-radius: 6px;
        }
        .column-header {
            font-weight: bold;
        }
        .scrollable-box {
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #CCC;
            padding: 8px;
            border-radius: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Features Box (top 1/3 of screen)
# -----------------------------
st.markdown("### Features")
st.markdown('<div class="container-box">', unsafe_allow_html=True)

cols = st.columns(len(other_df.columns))

for i, col_name in enumerate(other_df.columns):
    with cols[i]:
        st.markdown(f"<div class='column-header'>{col_name}</div>", unsafe_allow_html=True)
        st.caption("Description")  # Placeholder

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Dataset Box (left) and Overture Box (right)
# -----------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.markdown("### Dataset Box")
    st.markdown('<div class="scrollable-box">', unsafe_allow_html=True)
    st.dataframe(other_df.head(50), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown("### Overture Box")
    st.markdown('<div class="scrollable-box">', unsafe_allow_html=True)
    st.dataframe(overture_df.head(50), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

