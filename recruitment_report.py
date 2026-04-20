import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Recruitment Report",
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
        "<h1 style='margin:0;'>Recruitment Report</h1>",
        unsafe_allow_html=True
    )

# ======================
# REFRESH
# ======================
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# ======================
# LOAD DATA
# ======================
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
    return pd.read_csv(url)

@st.cache_data(ttl=60)
def load_mpp():
    url = "https://docs.google.com/spreadsheets/d/10A2o_8D_C5d0HWl1ve6WNn9V7AdSqSufLnWr3lKtR9I/export?format=csv&gid=0"
    return pd.read_csv(url)

df = load_data()
mpp = load_mpp()

if df.empty:
    st.warning("No data available")
    st.stop()

# ======================
# CLEANING
# ======================
df.columns = df.columns.str.lower()
mpp.columns = mpp.columns.str.lower()

for col in ["level", "position", "status", "loc"]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# =========================================================
# ================= RECRUITMENT SECTION ====================
# =========================================================

with st.expander("📊 Recruitment Database", expanded=True):

    st.subheader("Filter")

    col1, col2, col3 = st.columns(3)
    filtered_df = df.copy()

    if "level" in df.columns:
        lvl = col1.selectbox("Select Level", ["All"] + sorted(df["level"].unique()), key="main_level")
        if lvl != "All":
            filtered_df = filtered_df[filtered_df["level"] == lvl]

    if "position" in df.columns:
        pos = col2.selectbox("Select Position", ["All"] + sorted(df["position"].unique()), key="main_position")
        if pos != "All":
            filtered_df = filtered_df[filtered_df["position"] == pos]

    if "loc" in df.columns:
        loc = col3.selectbox("Select Location", ["All"] + sorted(df["loc"].unique()), key="main_loc")
        if loc != "All":
            filtered_df = filtered_df[filtered_df["loc"] == loc]

    st.subheader("Summary")

    k1, k2 = st.columns(2)
    k1.metric("Total Candidate", len(df))
    k2.metric("Filtered Candidate", len(filtered_df))

    st.subheader("Candidate Status")

    s1, s2, s3 = st.columns(3)

    if "status" in filtered_df.columns:
        status_series = filtered_df["status"].str.upper()

        s1.metric("On-Progress", (status_series == "OPEN").sum())
        s2.metric("Failed", (status_series == "FAILED").sum())
        s3.metric("Hiring", (status_series == "CLOSE").sum())

    st.subheader("Analytics")

    c1, c2 = st.columns(2)

    if "level" in filtered_df.columns:
        c1.bar_chart(filtered_df["level"].value_counts())

    if "position" in filtered_df.columns:
        c2.bar_chart(filtered_df["position"].value_counts())

    st.subheader("Data Detail")
    st.dataframe(filtered_df, use_container_width=True)

# =========================================================
# ====================== MPP SECTION ======================
# =========================================================

with st.expander("📈 MPP Dashboard", expanded=False):

    if mpp.empty:
        st.warning("MPP data gagal dimuat.")
    else:
        st.success("MPP Loaded ✅")

        f1, f2, f3 = st.columns(3)
        mpp_filtered = mpp.copy()

        if "level" in mpp.columns:
            lvl_sel = f1.selectbox("Level (MPP)", ["All"] + sorted(mpp["level"].dropna().unique()), key="mpp_level")
            if lvl_sel != "All":
                mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_sel]

        if "loc" in mpp.columns:
            loc_sel = f2.selectbox("Location (MPP)", ["All"] + sorted(mpp["loc"].dropna().unique()), key="mpp_loc")
            if loc_sel != "All":
                mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_sel]

        if "status" in mpp.columns:
            st_sel = f3.selectbox("Status (MPP)", ["All"] + sorted(mpp["status"].dropna().unique()), key="mpp_status")
            if st_sel != "All":
                mpp_filtered["status"] = mpp_filtered["status"].str.upper().str.strip()
                mpp_filtered = mpp_filtered[mpp_filtered["status"] == st_sel.upper()]

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

        st.dataframe(pivot, use_container_width=True)

# =========================================================
# ========== MPP vs RECRUITMENT PIPELINE ===================
# =========================================================

with st.expander("📊 MPP vs Recruitment Pipeline", expanded=False):

    st.subheader("Pipeline Analysis (By Departement)")

    col_d1, col_d2 = st.columns(2)
    start_date = col_d1.date_input("Start Date", key="pipe_start")
    end_date = col_d2.date_input("End Date", key="pipe_end")

    # ======================
    # SYNC FILTER (MPP → REC)
    # ======================
    df_pipeline = df.copy()

    # normalize text
    df_pipeline["status_position"] = df_pipeline["status_position"].astype(str).str.upper().str.strip()
    mpp_filtered["status"] = mpp_filtered["status"].astype(str).str.upper().str.strip()

    # filter by dept
    valid_dept = mpp_filtered["departement"].unique()
    df_pipeline = df_pipeline[df_pipeline["departement"].isin(valid_dept)]

    # filter by status
    valid_status = mpp_filtered["status"].unique()
    df_pipeline = df_pipeline[df_pipeline["status_position"].isin(valid_status)]

    # filter by level
    valid_level = mpp_filtered["level"].unique()
    df_pipeline = df_pipeline[df_pipeline["level"].isin(valid_level)]

    # filter by loc
    valid_loc = mpp_filtered["loc"].unique()
    df_pipeline = df_pipeline[df_pipeline["loc"].isin(valid_loc)]

    # ======================
    # DATE PREP
    # ======================
    date_cols = [
        "start_screening_cv",
        "start_interview_hr",
        "start_interview_user",
        "start_psychotest",
        "start_offering",
        "start_mcu",
        "start_review_mcu",
        "start_fu_mcu",
        "date_onboarding"
    ]

    for col in date_cols:
        if col in df_pipeline.columns:
            df_pipeline[col] = pd.to_datetime(df_pipeline[col], errors="coerce")

    # ======================
    # COUNT
    # ======================
    def count_stage(col_name):
        temp = df_pipeline[
            (df_pipeline[col_name] >= pd.to_datetime(start_date)) &
            (df_pipeline[col_name] <= pd.to_datetime(end_date))
        ]
        return temp.groupby("departement")[col_name].count()

    pipeline = pd.DataFrame()
    pipeline["Screening CV"] = count_stage("start_screening_cv")
    pipeline["HR Interview"] = count_stage("start_interview_hr")
    pipeline["User Interview"] = count_stage("start_interview_user")
    pipeline["Psychotest"] = count_stage("start_psychotest")
    pipeline["Offering"] = count_stage("start_offering")
    pipeline["MCU"] = count_stage("start_mcu")
    pipeline["Review MCU"] = count_stage("start_review_mcu")
    pipeline["FU MCU"] = count_stage("start_fu_mcu")
    pipeline["Onboarding"] = count_stage("date_onboarding")

    pipeline = pipeline.fillna(0)

    # ======================
    # MPP SUMMARY
    # ======================
    mpp_summary = mpp_filtered.groupby(["divisi", "departement"])[[
        "2026(r)",
        "2026(a)",
        "talent_management",
        "gap_fullfill_rec"
    ]].sum(numeric_only=True)

    mpp_summary = mpp_summary.rename(columns={
        "2026(r)": "MPP",
        "2026(a)": "Existing",
        "talent_management": "ADP 2026",
        "gap_fullfill_rec": "GAP"
    })

    # ======================
    # MERGE
    # ======================
    final_table = mpp_summary.merge(
        pipeline,
        left_on="departement",
        right_index=True,
        how="left"
    ).fillna(0)

    final_table = final_table.reset_index()

    st.dataframe(final_table, use_container_width=True)
