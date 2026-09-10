import datetime
import pandas as pd
import streamlit as st
from db import run_execute, run_query

st.set_page_config(page_title="Manage Records", page_icon="✏️", layout="wide")

st.title("✏️ Manage Records (All 19 Tables)")

# Password check
if not st.session_state.get("db_password"):
    st.warning("Please enter your MySQL root password on the Home page sidebar first.")
    st.stop()

st.write(
    "Select any of the **19 database tables** to test INSERT, UPDATE, or DELETE operations and observe MySQL constraint enforcement (Primary Keys, Foreign Keys, and CHECK constraints)."
)

TABLES = sorted([
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
])

selected_table = st.selectbox("Select Table to Manage:", TABLES)

if selected_table:
    # 1. RETRIEVE SCHEMA METADATA (Explicit aliases & lowercased columns to prevent KeyError)
    schema_sql = """
        SELECT 
            COLUMN_NAME AS column_name,
            DATA_TYPE AS data_type,
            COLUMN_KEY AS column_key,
            IS_NULLABLE AS is_nullable,
            COLUMN_DEFAULT AS column_default
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'smart_hospital' AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """
    df_schema = run_query(schema_sql, (selected_table,))

    if df_schema.empty:
        st.error(f"Could not load schema for table '{selected_table}'.")
        st.stop()

    # Normalize column names to lowercase to handle driver differences
    df_schema.columns = [str(c).lower() for c in df_schema.columns]

    cols = df_schema["column_name"].tolist()
    pk_rows = df_schema[df_schema["column_key"] == "PRI"]
    pk_col = pk_rows.iloc[0]["column_name"] if not pk_rows.empty else cols[0]

    # 2. CURRENT RECORDS PREVIEW
    st.subheader(f"Current Records in `{selected_table}` (Latest 50)")
    df_current = run_query(f"SELECT * FROM `{selected_table}` ORDER BY `{pk_col}` DESC LIMIT 50")
    st.dataframe(df_current, use_container_width=True, hide_index=True)

    # SAFE VALUE PARSER FOR PANDAS / STREAMLIT
    def safe_val(v):
        if pd.isna(v) or v is None:
            return None
        return v

    def render_col_input(row, default_val=None, key_prefix="ins"):
        c_name = row["column_name"]
        d_type = str(row["data_type"]).lower()
        is_pk = (row["column_key"] == "PRI")
        key = f"{key_prefix}_{selected_table}_{c_name}"
        val = safe_val(default_val)

        if "date" in d_type:
            date_val = datetime.date.today()
            if val is not None:
                try:
                    if isinstance(val, (datetime.date, datetime.datetime)):
                        date_val = val if isinstance(val, datetime.date) else val.date()
                    else:
                        date_val = datetime.datetime.strptime(str(val)[:10], "%Y-%m-%d").date()
                except Exception:
                    date_val = datetime.date.today()
            return st.date_input(f"`{c_name}` ({d_type})", value=date_val, key=key)

        elif any(t in d_type for t in ["int", "tinyint", "smallint", "mediumint", "bigint"]):
            int_val = 1 if (is_pk and val is None) else 0
            if val is not None:
                try:
                    int_val = int(val)
                except Exception:
                    int_val = 0
            return st.number_input(f"`{c_name}` ({d_type})", value=int_val, step=1, key=key)

        elif any(t in d_type for t in ["decimal", "float", "double", "numeric"]):
            float_val = 0.0
            if val is not None:
                try:
                    float_val = float(val)
                except Exception:
                    float_val = 0.0
            return st.number_input(f"`{c_name}` ({d_type})", value=float_val, step=1.0, format="%.2f", key=key)

        else:
            str_val = "" if val is None else str(val)
            return st.text_input(f"`{c_name}` ({d_type})", value=str_val, key=key)

    # 3. TABS FOR INSERT, UPDATE, DELETE
    tab_insert, tab_update, tab_delete = st.tabs([
        "➕ Insert New Record",
        "✏️ Update Existing Record",
        "🗑️ Delete Record",
    ])

    # --- TAB 1: INSERT ---
    with tab_insert:
        st.header(f"Insert Record into `{selected_table}`")
        with st.form(f"form_ins_{selected_table}"):
            ins_inputs = {}
            for _, r in df_schema.iterrows():
                ins_inputs[r["column_name"]] = render_col_input(r, key_prefix="ins")

            submit_ins = st.form_submit_button("Submit INSERT Operation")
            if submit_ins:
                cols_str = ", ".join([f"`{c}`" for c in cols])
                placeholders = ", ".join(["%s"] * len(cols))
                sql_ins = f"INSERT INTO `{selected_table}` ({cols_str}) VALUES ({placeholders})"
                params = tuple(ins_inputs[c] for c in cols)

                success, msg = run_execute(sql_ins, params)
                if success:
                    st.success(f"Successfully inserted row into `{selected_table}`! Affected rows: {msg}")
                    st.rerun()
                else:
                    st.error(f"INSERT Rejected by MySQL (Constraint Enforcement Working):\n{msg}")

    # --- TAB 2: UPDATE ---
    with tab_update:
        st.header(f"Update Record in `{selected_table}`")
        existing_ids = df_current[pk_col].tolist() if (not df_current.empty and pk_col in df_current.columns) else []

        upd_target_id = st.number_input(
            f"Enter {pk_col} to Update:",
            min_value=1,
            value=int(existing_ids[0]) if existing_ids else 1,
            step=1,
            key=f"upd_target_id_{selected_table}",
        )

        df_target = run_query(f"SELECT * FROM `{selected_table}` WHERE `{pk_col}` = %s", (upd_target_id,))

        if df_target.empty:
            st.warning(f"No record found in `{selected_table}` where `{pk_col}` = {upd_target_id}.")
        else:
            target_row = df_target.iloc[0]
            st.write(f"Editing Record Primary Key `{pk_col}` = **{upd_target_id}**:")

            with st.form(f"form_upd_{selected_table}"):
                upd_inputs = {}
                non_pk_schema = df_schema[df_schema["column_name"] != pk_col]

                for _, r in non_pk_schema.iterrows():
                    c_name = r["column_name"]
                    upd_inputs[c_name] = render_col_input(r, default_val=target_row[c_name], key_prefix="upd")

                submit_upd = st.form_submit_button("Submit UPDATE Operation")
                if submit_upd:
                    set_clause = ", ".join([f"`{c}` = %s" for c in upd_inputs.keys()])
                    sql_upd = f"UPDATE `{selected_table}` SET {set_clause} WHERE `{pk_col}` = %s"
                    params = tuple(upd_inputs[c] for c in upd_inputs.keys()) + (upd_target_id,)

                    success, msg = run_execute(sql_upd, params)
                    if success:
                        st.success(f"Successfully updated record `{pk_col}` = {upd_target_id}! Affected rows: {msg}")
                        st.rerun()
                    else:
                        st.error(f"UPDATE Rejected by MySQL (Constraint Enforcement Working):\n{msg}")

    # --- TAB 3: DELETE ---
    with tab_delete:
        st.header(f"Delete Record from `{selected_table}`")
        existing_ids_del = df_current[pk_col].tolist() if (not df_current.empty and pk_col in df_current.columns) else []

        del_target_id = st.number_input(
            f"Enter {pk_col} to Delete:",
            min_value=1,
            value=int(existing_ids_del[0]) if existing_ids_del else 1,
            step=1,
            key=f"del_target_id_{selected_table}",
        )

        st.caption("Note: Deleting records referenced by foreign keys in other tables will trigger MySQL Foreign Key RESTRICT rejection.")

        with st.form(f"form_del_{selected_table}"):
            submit_del = st.form_submit_button(f"Confirm DELETE Record ({pk_col} = {del_target_id})")
            if submit_del:
                sql_del = f"DELETE FROM `{selected_table}` WHERE `{pk_col}` = %s"
                success, msg = run_execute(sql_del, (del_target_id,))

                if success:
                    st.success(f"Successfully deleted record `{pk_col}` = {del_target_id}! Affected rows: {msg}")
                    st.rerun()
                else:
                    st.error(f"DELETE Rejected by MySQL (Foreign Key RESTRICT Working):\n{msg}")
