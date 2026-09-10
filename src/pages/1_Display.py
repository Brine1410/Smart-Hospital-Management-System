import pandas as pd
import streamlit as st
from db import run_query

st.set_page_config(page_title="Display Dashboard", page_icon="🖥️", layout="wide")

st.title("🖥️ SMART HOSPITAL SYSTEM — Display Dashboard")

# Password check
if not st.session_state.get("db_password"):
    st.warning("Please enter your MySQL root password on the Home page sidebar first.")
    st.stop()

# 1. TOP METRICS ROW
col1, col2, col3, col4 = st.columns(4)

df_p = run_query("SELECT COUNT(*) AS cnt FROM patient")
patients_cnt = int(df_p.iloc[0]["cnt"]) if not df_p.empty else 0

df_d = run_query("SELECT COUNT(*) AS cnt FROM doctor")
doctors_cnt = int(df_d.iloc[0]["cnt"]) if not df_d.empty else 0

# Calculate active admissions (currently occupied beds where discharge_date IS NULL)
df_active_adm = run_query("SELECT COUNT(*) AS cnt FROM admission WHERE discharge_date IS NULL OR admission_status = 'Admitted'")
active_admissions = int(df_active_adm.iloc[0]["cnt"]) if not df_active_adm.empty else 0

df_b = run_query("SELECT COUNT(*) AS total FROM bed")
total_beds = int(df_b.iloc[0]["total"]) if not df_b.empty else 0

occupied_beds = min(active_admissions, total_beds)
avail_beds = total_beds - occupied_beds

df_e = run_query("SELECT COUNT(*) AS cnt FROM admission WHERE admission_type = 'Emergency'")
emergency_cnt = int(df_e.iloc[0]["cnt"]) if not df_e.empty else 0

col1.metric("PATIENTS", f"{patients_cnt:,}")
col2.metric("DOCTORS", f"{doctors_cnt:,}")
col3.metric("BEDS (AVAILABLE)", f"{avail_beds:,} / {total_beds:,}")
col4.metric("EMERGENCY CASES", f"{emergency_cnt:,}")

st.info(
    f"ℹ️ **Bed Status Note**: The database contains 45,000 historical admission records. "
    f"Beds are marked occupied when an admission is active (`discharge_date IS NULL`). "
    f"Currently, **{occupied_beds}** beds are occupied and **{avail_beds}** beds are available."
)

st.write("---")

# 2. PATIENTS BY DEPARTMENT & BED STATUS
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📊 PATIENTS BY DEPARTMENT")
    sql_dept_patients = """
        SELECT 
            dept.department_name AS Department,
            COUNT(a.admission_id) AS `Patients Count`
        FROM department dept
        LEFT JOIN admission a ON dept.department_id = a.department_id
        GROUP BY dept.department_id, dept.department_name
        ORDER BY `Patients Count` DESC;
    """
    df_dept_patients = run_query(sql_dept_patients)
    if not df_dept_patients.empty:
        st.dataframe(df_dept_patients, use_container_width=True, hide_index=True)
        chart_data = df_dept_patients.set_index("Department")["Patients Count"]
        st.bar_chart(chart_data)

with right_col:
    st.subheader("🛏️ BED STATUS BY WARD TYPE")
    sql_bed_status = """
        SELECT 
            w.ward_type AS `Ward Type`,
            COUNT(DISTINCT w.ward_id) AS `Total Wards`,
            COUNT(DISTINCT b.bed_id) AS `Total Beds`,
            COUNT(DISTINCT CASE WHEN a.admission_id IS NOT NULL AND a.discharge_date IS NULL THEN a.bed_id END) AS `Occupied Beds`,
            (COUNT(DISTINCT b.bed_id) - COUNT(DISTINCT CASE WHEN a.admission_id IS NOT NULL AND a.discharge_date IS NULL THEN a.bed_id END)) AS `Available Beds`
        FROM ward w
        JOIN bed b ON w.ward_id = b.ward_id
        LEFT JOIN admission a ON b.bed_id = a.bed_id AND a.discharge_date IS NULL
        GROUP BY w.ward_type
        ORDER BY `Total Beds` DESC;
    """
    df_bed_status = run_query(sql_bed_status)
    if not df_bed_status.empty:
        st.dataframe(df_bed_status, use_container_width=True, hide_index=True)
        
        st.write("**Bed Availability Summary:**")
        for _, row in df_bed_status.iterrows():
            st.text(f"• {row['Ward Type']} ({row['Total Wards']} Wards): {row['Available Beds']:,} available ({row['Occupied Beds']:,} occupied / {row['Total Beds']:,} total)")

        # UNSTACKED SIDE-BY-SIDE BAR CHART FOR BEDS
        st.subheader("📈 Bed Capacity vs. Availability (Side-by-Side)")
        bed_chart_df = df_bed_status.set_index("Ward Type")[["Total Beds", "Available Beds", "Occupied Beds"]]
        st.bar_chart(bed_chart_df, stack=False)

st.write("---")

# 3. RECENT EMERGENCY CASES TABLE
st.subheader("🚨 RECENT EMERGENCY CASES")

sql_recent_emergency = """
    SELECT 
        a.admission_id AS `Admission ID`,
        a.admission_date AS `Admission Date`,
        a.patient_id AS `Patient ID`,
        dept.department_name AS `Department`,
        w.ward_name AS `Ward`,
        b.bed_number AS `Bed #`,
        a.admission_status AS `Status`
    FROM admission a
    JOIN department dept ON a.department_id = dept.department_id
    JOIN ward w ON a.ward_id = w.ward_id
    JOIN bed b ON a.bed_id = b.bed_id
    WHERE a.admission_type = 'Emergency'
    ORDER BY a.admission_date DESC, a.admission_id DESC
    LIMIT 15;
"""

df_recent_emergency = run_query(sql_recent_emergency)
if not df_recent_emergency.empty:
    st.dataframe(df_recent_emergency, use_container_width=True, hide_index=True)
else:
    st.write("No emergency cases recorded.")
