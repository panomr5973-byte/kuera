"""
Streamlit Application
=====================
Contoh aplikasi Streamlit untuk demo model.
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="AI Project Demo",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Project Demo")
st.markdown("---")

# Sidebar
st.sidebar.header("Settings")
model_option = st.sidebar.selectbox(
    "Select Model",
    ["Random Forest", "XGBoost", "LightGBM"]
)

# Main content
st.header("📊 Data Overview")

# Sample data upload
uploaded_file = st.file_uploader("Upload your data (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:")
    st.dataframe(df.head())
    
    st.write("Data Statistics:")
    st.write(df.describe())

# Model prediction section
st.header("🎯 Model Prediction")

if st.button("Run Prediction"):
    with st.spinner("Running prediction..."):
        # Placeholder for actual prediction
        st.success("Prediction completed!")
        st.info(f"Model used: {model_option}")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")

if __name__ == "__main__":
    print("Run with: streamlit run app/app.py")
