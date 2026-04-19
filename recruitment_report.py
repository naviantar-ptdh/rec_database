import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Recruitment Dashboard",
    layout="wide"
)

st.title("Recruitment Dashboard")


col_logo, col_title = st.columns([1, 8])

with col_logo:
    st.image("logo_solid.png", width=100)

with col_title:
    st.markdown(
        "<h1 style='padding-top:20px;'>Recruitment Dashboard</h1>",
        unsafe_allow_html=True
    )

# ======================
# CONNECT GOOGLE SHEETS
# ======================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_data():
    df = conn.read(
        spreadsheet="1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc"
    )
    return df

df = load_data()

# ======================
# DATA CLEANING
# ======================
if df.empty:
    st.warning("No data available")
    st.stop()

df.columns = df.columns.str.lower()

if "level" in df.columns:
    df["level"] = df["level"].fillna("Unknown")

if "position" in df.columns:
    df["position"] = df["position"].fillna("Unknown")

# ======================
# FILTER SECTION (TOP DROPDOWN)
# ======================
st.subheader("Filter")

col1, col2 = st.columns(2)

filtered_df = df.copy()

# FILTER LEVEL
if "level" in df.columns:
    level_options = sorted(df["level"].dropna().unique())

    selected_level = col1.selectbox(
        "Select Level",
        ["All"] + level_options
    )

    if selected_level != "All":
        filtered_df = filtered_df[
            filtered_df["level"] == selected_level
        ]

# FILTER POSITION
if "position" in df.columns:
    pos_options = sorted(df["position"].dropna().unique())

    selected_pos = col2.selectbox(
        "Select Position",
        ["All"] + pos_options
    )

    if selected_pos != "All":
        filtered_df = filtered_df[
            filtered_df["position"] == selected_pos
        ]

# ======================
# KPI SECTION
# ======================
st.subheader("Summary")

k1, k2, k3 = st.columns(3)

k1.metric("Total Candidate", len(df))
k2.metric("Filtered Candidate", len(filtered_df))

if "level" in filtered_df.columns:
    k3.metric("Unique Level", filtered_df["level"].nunique())
else:
    k3.metric("Unique Level", "-")

# ======================
# ANALYTICS
# ======================
st.subheader("Analytics")

c1, c2 = st.columns(2)

if "level" in filtered_df.columns:
    c1.bar_chart(filtered_df["level"].value_counts())

if "position" in filtered_df.columns:
    c2.bar_chart(filtered_df["position"].value_counts())

# ======================
# DATA TABLE
# ======================
st.subheader("Data Detail")

st.dataframe(filtered_df, use_container_width=True)
