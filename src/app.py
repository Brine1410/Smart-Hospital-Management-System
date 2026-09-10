import pandas as pd
import streamlit as st
from db import get_connection, run_query

st.set_page_config(
    page_title="Smart Hospital Management System",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Smart Hospital Management System")

st.sidebar.header("Database Connection")

default_password = st.session_state.get("db_password", "")
db_password = st.sidebar.text_input(
    "MySQL root password",
    value=default_password,
    type="password",
)

if db_password:
    st.session_state["db_password"] = db_password

if not st.session_state.get("db_password"):
    st.info("Enter your MySQL root password in the sidebar to continue.")
    st.stop()

# Test connection
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
- **1 Browse Tables**: Inspect column data types and browse rows for all 19 relational tables.
- **2 SQL Queries**: Execute prebuilt complex queries (3+ JOINs, Window functions, Subqueries, Aggregates) or test custom SELECT queries.
- **3 Search**: Lookup patient profiles and view linked clinical, pharmacy, diagnostic, insurance, and billing records.
- **4 Manage Records**: Test CRUD operations and witness MySQL constraint enforcement (PK, FK, CHECK).
- **5 Schema**: Inspect Foreign Keys, CHECK constraints, and full DDL script.
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