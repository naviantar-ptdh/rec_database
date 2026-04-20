# =========================================================
# ========== MPP vs RECRUITMENT PIPELINE ===================
# =========================================================

with st.expander("📊 MPP vs Recruitment Pipeline", expanded=False):

    st.subheader("Pipeline Analysis (By Departement)")

    # ======================
    # DATE FILTER
    # ======================
    col_d1, col_d2 = st.columns(2)

    start_date = col_d1.date_input("Start Date", key="pipe_start")
    end_date = col_d2.date_input("End Date", key="pipe_end")

    # ======================
    # FILTER MPP (GLOBAL FILTER 🔥)
    # ======================
    f1, f2, f3 = st.columns(3)

    mpp_filtered = mpp.copy()

    # default value biar aman
    lvl_mpp = "All"
    loc_mpp = "All"
    st_mpp = "All"

    if "level" in mpp_filtered.columns:
        lvl_mpp = f1.selectbox(
            "Level", 
            ["All"] + sorted(mpp_filtered["level"].dropna().unique()), 
            key="pipe_mpp_level"
        )
        if lvl_mpp != "All":
            mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_mpp]

    if "loc" in mpp_filtered.columns:
        loc_mpp = f2.selectbox(
            "Location", 
            ["All"] + sorted(mpp_filtered["loc"].dropna().unique()), 
            key="pipe_mpp_loc"
        )
        if loc_mpp != "All":
            mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_mpp]

    if "status" in mpp_filtered.columns:
        st_mpp = f3.selectbox(
            "Status", 
            ["All"] + sorted(mpp_filtered["status"].dropna().unique()), 
            key="pipe_mpp_status"
        )
        if st_mpp != "All":
            mpp_filtered = mpp_filtered[
                mpp_filtered["status"].str.upper() == st_mpp.upper()
            ]

    # ======================
    # APPLY FILTER KE REC 🔥
    # ======================
    df_pipeline = df.copy()

    if "level" in df_pipeline.columns and lvl_mpp != "All":
        df_pipeline = df_pipeline[df_pipeline["level"] == lvl_mpp]

    if "loc" in df_pipeline.columns and loc_mpp != "All":
        df_pipeline = df_pipeline[df_pipeline["loc"] == loc_mpp]

    if "status" in df_pipeline.columns and st_mpp != "All":
        df_pipeline = df_pipeline[
            df_pipeline["status"].str.upper() == st_mpp.upper()
        ]

    # ======================
    # PREPARE DATE
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
    # COUNT FUNCTION
    # ======================
    def count_stage(col_name):
        if col_name not in df_pipeline.columns:
            return pd.Series(dtype=float)

        temp = df_pipeline[
            (df_pipeline[col_name] >= pd.to_datetime(start_date)) &
            (df_pipeline[col_name] <= pd.to_datetime(end_date))
        ]

        return temp.groupby("departement")[col_name].count()

    # ======================
    # PIPELINE
    # ======================
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
    mpp_dept = mpp_filtered.copy()
    mpp_dept.columns = mpp_dept.columns.str.lower()

    mpp_summary = mpp_dept.groupby(["divisi", "departement"])[[
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

    # ======================
    # OUTPUT
    # ======================
    st.dataframe(final_table, use_container_width=True)
