import pandas as pd
import streamlit as st
from db import get_connection, run_query

st.title("🏥 Smart Hospital Management System")

# Test connection & Password check
if not st.session_state.get("db_password"):
    st.info("Enter your MySQL root password in the sidebar to continue.")
    st.stop()

try:
    conn = get_connection()
    conn.close()
    st.success("Connected to MySQL database 'smart_hospital' successfully.")
except Exception as err:
    st.error(f"Database connection failed: {err}")
    st.stop()

st.header("Project Overview")
st.write(
    """
Welcome to the **Smart Hospital Management System** database demonstration app. 
This application provides an interactive interface for exploring, querying, and managing 
the relational hospital dataset stored in MySQL 8.

### Navigation Overview
- ● **Home**: System overview and database-wide 19-table row count summary.
- ● **Display**: Operational dashboard displaying patient metrics, doctor counts, bed availability, patients by department, and recent emergency cases.
- ● **Search**: Lookup patient profiles and view linked clinical, pharmacy, diagnostic, insurance, and billing records.
- ● **Browse Tables**: Inspect column data types, browse rows, and view maximum rows for all 19 relational tables.
- ● **Manage Records**: Perform INSERT, UPDATE, and DELETE operations across **all 19 tables** and witness MySQL constraint enforcement (PK, FK, CHECK).
- ● **SQL Queries**: Execute prebuilt complex queries (3+ JOINs, Window functions, Subqueries, Aggregates) or test custom SELECT queries.
- ● **Schema**: Inspect Foreign Keys, CHECK constraints, and full DDL script.
"""
)

st.header("Database Summary (19 Tables)")

TABLES = [
    "admission",
    "bed",
    "billing",
    "billing_detail",
    "department",
    "diagnostic_test",
    "disease",
    "doctor",
    "drug",
    "drug_inventory",
    "drug_manufacturer",
    "employee",
    "insurance_provider",
    "patient",
    "patient_diagnostic",
    "patient_insurance",
    "prescription",
    "staff_assignment",
    "ward",
]

counts = []
for table in TABLES:
    df_count = run_query(f"SELECT COUNT(*) AS row_count FROM `{table}`")
    if not df_count.empty:
        counts.append(
            {"Table Name": table, "Total Rows": int(df_count.iloc[0]["row_count"])}
        )

if counts:
    df_summary = pd.DataFrame(counts)
    total_rows = df_summary["Total Rows"].sum()
    st.subheader(f"Total Rows Across Database: {total_rows:,}")
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
