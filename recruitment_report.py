import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

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
# REFRESH BUTTON
# ======================
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# ======================
# LOAD MAIN DATA (CSV)
# ======================
@st.cache_data(ttl=60)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error load main data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data available")
    st.stop()

df.columns = df.columns.str.lower()

for col in ["level", "position", "status", "loc"]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# ======================
# FILTER MAIN
# ======================
st.subheader("Filter")

col1, col2, col3 = st.columns(3)
filtered_df = df.copy()

if "level" in df.columns:
    lvl = col1.selectbox(
        "Select Level",
        ["All"] + sorted(df["level"].unique()),
        key="main_level"
    )
    if lvl != "All":
        filtered_df = filtered_df[filtered_df["level"] == lvl]

if "position" in df.columns:
    pos = col2.selectbox(
        "Select Position",
        ["All"] + sorted(df["position"].unique()),
        key="main_position"
    )
    if pos != "All":
        filtered_df = filtered_df[filtered_df["position"] == pos]

if "loc" in df.columns:
    loc = col3.selectbox(
        "Select Location",
        ["All"] + sorted(df["loc"].unique()),
        key="main_loc"
    )
    if loc != "All":
        filtered_df = filtered_df[filtered_df["loc"] == loc]

# ======================
# KPI
# ======================
st.subheader("Summary")

k1, k2 = st.columns(2)
k1.metric("Total Candidate", len(df))
k2.metric("Filtered Candidate", len(filtered_df))

# STATUS KPI
st.subheader("Candidate Status")

s1, s2, s3 = st.columns(3)

if "status" in filtered_df.columns:
    status_series = filtered_df["status"].str.upper()

    s1.metric("On-Progress", (status_series == "OPEN").sum())
    s2.metric("Failed", (status_series == "FAILED").sum())
    s3.metric("Hiring", (status_series == "CLOSE").sum())

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
# TABLE
# ======================
st.subheader("Data Detail")
st.dataframe(filtered_df, use_container_width=True)

# =========================================================
# ====================== MPP SECTION ======================
# =========================================================

st.divider()
st.header("MPP Dashboard")

# ======================
# LOAD MPP (CSV METHOD)
# ======================
@st.cache_data(ttl=60)
def load_mpp():
    try:
        url = "https://docs.google.com/spreadsheets/d/10A2o_8D_C5d0HWl1ve6WNn9V7AdSqSufLnWr3lKtR9I/export?format=csv&gid=0"
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error load MPP: {e}")
        return pd.DataFrame()

mpp = load_mpp()

if mpp.empty:
    st.warning("MPP data gagal dimuat. Cek sharing & gid.")
else:
    st.success("MPP Loaded ✅")

    mpp.columns = mpp.columns.str.lower()

    # ======================
    # FILTER MPP
    # ======================
    f1, f2 = st.columns(2)
    mpp_filtered = mpp.copy()

    if "loc" in mpp.columns:
        loc_opt = ["All"] + sorted(mpp["loc"].dropna().unique())
        loc_sel = f1.selectbox(
            "Select Location (MPP)",
            loc_opt,
            key="mpp_loc"
        )

        if loc_sel != "All":
            mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_sel]

    if "level" in mpp.columns:
        lvl_opt = ["All"] + sorted(mpp["level"].dropna().unique())
        lvl_sel = f2.selectbox(
            "Select Level (MPP)",
            lvl_opt,
            key="mpp_level"
        )

        if lvl_sel != "All":
            mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_sel]

    # ======================
    # PIVOT
    # ======================
    try:
        pivot_df = mpp_filtered[[
            "divisi",
            "2026(r)",
            "2026(a)",
            "talent_management",
            "gap_fullfill_rec"
        ]].copy()

        pivot_df = pivot_df.rename(columns={
            "2026(r)": "MPP",
            "2026(a)": "Existing",
            "talent_management": "ADP_2026",
            "gap_fullfill_rec": "GAP"
        })

        pivot = pivot_df.groupby("divisi").sum(numeric_only=True)

        pivot["TOTAL"] = pivot.sum(axis=1)

        st.dataframe(
            pivot.style.format("{:,.0f}"),
            use_container_width=True
        )

        # ======================
        # EXPORT IMAGE
        # ======================
        def create_table_image(df):
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.axis('off')

            table = ax.table(
                cellText=df.values,
                colLabels=df.columns,
                rowLabels=df.index,
                loc='center'
            )

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)

            buf = io.BytesIO()
            plt.savefig(buf, bbox_inches='tight')
            buf.seek(0)
            return buf

        img = create_table_image(pivot)

        st.download_button(
            label="Download MPP as Image",
            data=img,
            file_name="mpp_pivot.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"Error saat pivot: {e}")
