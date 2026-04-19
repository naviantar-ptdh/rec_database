import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Recruitment Dashboard (Google Sheets)")

# connect
conn = st.connection("gsheets", type=GSheetsConnection)

# read data
df = conn.read(
    spreadsheet="https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc",
)

# display
st.dataframe(df)

# KPI simple
st.metric("Total Candidate", len(df))

# filter
if "level" in df.columns:
    level = st.selectbox("Select Level", sorted(df["level"].dropna().unique()))
    filtered_df = df[df["level"] == level]
    st.dataframe(filtered_df)
