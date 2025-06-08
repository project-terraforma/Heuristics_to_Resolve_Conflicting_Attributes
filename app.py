import streamlit as st
import pandas as pd

# Load datasets
other_df = pd.read_csv("other_dataset.csv")
overture_df = pd.read_csv("overture_data.csv")

# Sidebar
with st.sidebar:
    st.title("Datasets")
    st.markdown("- other_dataset.csv")
    st.markdown("- overture_data.csv")
    st.markdown("---")
    if st.button("+", help="Add new dataset"):
        st.info("Add dataset functionality not implemented.")

# Main layout
st.markdown(
    """
    <style>
        .feature-box {
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 20px;
            height: 33vh;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        .scroll-box {
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 10px;
            height: 60vh;
            overflow-y: scroll;
        }
        .column-block {
            display: inline-block;
            margin-right: 20px;
            vertical-align: top;
        }
        .column-title {
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Features Box
st.markdown("### Features Box")
st.markdown('<div class="feature-box">', unsafe_allow_html=True)

for col in other_df.columns:
    st.markdown(f"<div class='column-block'><div class='column-title'>{col}</div><div>Description</div></div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Second Row Layout: Two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Dataset Box")
    st.markdown('<div class="scroll-box">', unsafe_allow_html=True)
    st.dataframe(other_df.head(50), height=400, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### Overture Box")
    st.markdown('<div class="scroll-box">', unsafe_allow_html=True)
    st.dataframe(overture_df.head(50), height=400, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

