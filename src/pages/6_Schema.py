import os
import streamlit as st
import pandas as pd
from db import run_query

st.set_page_config(page_title="Database Schema", page_icon="🏗️", layout="wide")

st.title("🏗️ Database Schema & Constraints")

# Password check
if not st.session_state.get("db_password"):
    st.warning("Please enter your MySQL root password on the Home page sidebar first.")
    st.stop()

st.write(
    "Inspect the schema relationships, Foreign Key dependencies, and CHECK constraint expressions defined in `INFORMATION_SCHEMA` for the `smart_hospital` database."
)

# 1. FOREIGN KEYS METADATA
st.header("1. Foreign Key Relationships")

fk_sql = """
    SELECT 
        TABLE_NAME AS `Table`,
        COLUMN_NAME AS `Column`,
        CONSTRAINT_NAME AS `FK Constraint Name`,
        REFERENCED_TABLE_NAME AS `Referenced Table`,
        REFERENCED_COLUMN_NAME AS `Referenced Column`
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'smart_hospital'
      AND REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY TABLE_NAME, CONSTRAINT_NAME;
"""

df_fk = run_query(fk_sql)
st.write(f"Total Foreign Key Constraints: **{len(df_fk)}**")
st.dataframe(df_fk, use_container_width=True, hide_index=True)

st.write("---")

# 2. CHECK CONSTRAINTS METADATA
st.header("2. CHECK Constraints")

check_sql = """
    SELECT 
        tc.TABLE_NAME AS `Table Name`,
        cc.CONSTRAINT_NAME AS `Constraint Name`,
        cc.CHECK_CLAUSE AS `Check Expression`
    FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS cc
    JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc 
      ON cc.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA 
     AND cc.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
    WHERE cc.CONSTRAINT_SCHEMA = 'smart_hospital'
    ORDER BY tc.TABLE_NAME, cc.CONSTRAINT_NAME;
"""

df_check = run_query(check_sql)
st.write(f"Total CHECK Constraints: **{len(df_check)}**")
st.dataframe(df_check, use_container_width=True, hide_index=True)

st.write("---")

# 3. RAW SQL SCHEMA FILE
st.header("3. Raw DDL Script")

sql_file_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "database",
    "smart_hospital_database.sql",
)

if os.path.exists(sql_file_path):
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_ddl = f.read()

    with st.expander("View Full Database Creation SQL Script (`smart_hospital_database.sql`)"):
        st.code(sql_ddl, language="sql")
else:
    st.info("Schema DDL file `database/smart_hospital_database.sql` not found.")
