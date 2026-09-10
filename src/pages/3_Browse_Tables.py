import pandas as pd
import streamlit as st
from db import run_query

st.set_page_config(page_title="Browse Tables", page_icon="📋", layout="wide")

st.title("📋 Browse Tables")

# Password check
if not st.session_state.get("db_password"):
    st.warning("Please enter your MySQL root password on the Home page sidebar first.")
    st.stop()

TABLES = sorted(
    [
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
)

selected_table = st.selectbox("Select Table:", TABLES)

if selected_table:
    # 1. Total row count
    count_df = run_query(f"SELECT COUNT(*) AS total_rows FROM `{selected_table}`")
    total_rows = 0
    if not count_df.empty:
        total_rows = int(count_df.iloc[0]["total_rows"])

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Selected Table", selected_table)
    col_m2.metric("Total / Maximum Rows in Table", f"{total_rows:,}")

    # 2. Column Metadata
    st.header(f"Columns & Data Types (`{selected_table}`)")
    schema_sql = """
        SELECT 
            column_name AS `Column Name`,
            data_type AS `Data Type`,
            column_type AS `Full Type`,
            is_nullable AS `Nullable`,
            column_key AS `Key`,
            column_default AS `Default Value`
        FROM information_schema.columns 
        WHERE table_schema = 'smart_hospital' AND table_name = %s
        ORDER BY ordinal_position
    """
    schema_df = run_query(schema_sql, (selected_table,))
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

    # 3. Table Rows Preview
    st.header(f"Table Data Preview (`{selected_table}`)")

    show_max = st.checkbox(
        f"Show Maximum Rows ({total_rows:,} total rows)",
        value=False,
        help=f"Check this box to fetch all {total_rows:,} rows from `{selected_table}`.",
    )

    if show_max:
        n_rows = total_rows
        st.success(f"Displaying maximum available dataset ({n_rows:,} rows).")
    else:
        max_val = total_rows if total_rows > 0 else 500
        n_rows = st.number_input(
            f"Number of rows to display (Max: {total_rows:,}):",
            min_value=1,
            max_value=max_val,
            value=min(50, max_val),
            step=50,
        )

    data_sql = f"SELECT * FROM `{selected_table}` LIMIT %s"
    data_df = run_query(data_sql, (int(n_rows),))
    st.dataframe(data_df, use_container_width=True, hide_index=True)
