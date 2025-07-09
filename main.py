import streamlit as st
import pandas as pd

st.title("📊 Amazon Sale AI Dashboard")

# Load processed data
df = pd.read_csv("data/processed/fab_tv_sale_sentiment.csv")

# Show basic info
st.write("### Sample Data", df.head())

# Show sentiment distribution
st.write("### Sentiment Distribution")
st.bar_chart(df["sentiment"].value_counts())

# Add any other visualizations you want
