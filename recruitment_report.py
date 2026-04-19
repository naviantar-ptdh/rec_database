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

st.title("📊 Recruitment Dashboard")

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

# standarize column name (optional)
df.columns = df.columns.str.lower()

# handle missing value
if "level" in df.columns:
    df["level"] = df["level"].fillna("Unknown")

if "position" in df.columns:
    df["position"] = df["position"].fillna("Unknown")

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔎 Filter")

filtered_df = df.copy()

# FILTER LEVEL
if "level" in df.columns:
    level_options = sorted(df["level"].dropna().unique())

    selected_levels = st.sidebar.multiselect(
        "Level",
        level_options,
        default=level_options
    )

    filtered_df = filtered_df[
        filtered_df["level"].isin(selected_levels)
    ]

# FILTER POSITION
if "position" in df.columns:
    pos_options = sorted(df["position"].dropna().unique())

    selected_pos = st.sidebar.multiselect(
        "Position",
        pos_options,
        default=pos_options
    )

    filtered_df = filtered_df[
        filtered_df["position"].isin(selected_pos)
    ]

# ======================
# KPI SECTION
# ======================
st.subheader("📈 Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Candidate", len(df))
col2.metric("Filtered Candidate", len(filtered_df))

# contoh KPI tambahan
if "level" in df.columns:
    col3.metric("Unique Level", filtered_df["level"].nunique())
else:
    col3.metric("Unique Level", "-")

# ======================
# SIMPLE ANALYTICS
# ======================
st.subheader("📊 Analytics")

col1, col2 = st.columns(2)

# COUNT BY LEVEL
if "level" in filtered_df.columns:
    level_count = filtered_df["level"].value_counts()

    col1.bar_chart(level_count)

# COUNT BY POSITION
if "position" in filtered_df.columns:
    pos_count = filtered_df["position"].value_counts()

    col2.bar_chart(pos_count)

# ======================
# DATA TABLE
# ======================
st.subheader("📋 Data Detail")

st.dataframe(filtered_df, use_container_width=True)
