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

# ======================
# HEADER
# ======================
col_logo, col_title = st.columns([1, 8], vertical_alignment="center")

with col_logo:
    st.image("logo_solid.png", width=70)

with col_title:
    st.markdown(
        "<h1 style='margin:0;'>Recruitment Dashboard</h1>",
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

for col in ["level", "position", "status", "loc"]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# ======================
# FILTER SECTION
# ======================
st.subheader("Filter")

col1, col2, col3 = st.columns(3)
filtered_df = df.copy()

# FILTER LEVEL
if "level" in df.columns:
    level_options = sorted(df["level"].unique())

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
    pos_options = sorted(df["position"].unique())

    selected_pos = col2.selectbox(
        "Select Position",
        ["All"] + pos_options
    )

    if selected_pos != "All":
        filtered_df = filtered_df[
            filtered_df["position"] == selected_pos
        ]

# FILTER LOCATION (LOC)
if "loc" in df.columns:
    loc_options = sorted(df["loc"].unique())

    selected_loc = col3.selectbox(
        "Select Location",
        ["All"] + loc_options
    )

    if selected_loc != "All":
        filtered_df = filtered_df[
            filtered_df["loc"] == selected_loc
        ]

# ======================
# KPI SECTION
# ======================
st.subheader("Summary")

k1, k2 = st.columns(2)

k1.metric("Total Candidate", len(df))
k2.metric("Filtered Candidate", len(filtered_df))

# ======================
# STATUS KPI
# ======================
st.subheader("Candidate Status")

s1, s2, s3 = st.columns(3)

if "status" in filtered_df.columns:
    status_series = filtered_df["status"].str.upper()

    on_progress = (status_series == "OPEN").sum()
    failed = (status_series == "FAILED").sum()
    hiring = (status_series == "CLOSE").sum()

    s1.metric("On-Progress", on_progress)
    s2.metric("Failed", failed)
    s3.metric("Hiring", hiring)
else:
    s1.metric("On-Progress", "-")
    s2.metric("Failed", "-")
    s3.metric("Hiring", "-")

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
