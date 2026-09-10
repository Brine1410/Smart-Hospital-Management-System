import streamlit as st
import pandas as pd
from db import run_query, run_execute

st.set_page_config(page_title="Manage Records", page_icon="✏️", layout="wide")

st.title("✏️ Manage Records (Constraint Enforcement)")

# Password check
if not st.session_state.get("db_password"):
    st.warning("Please enter your MySQL root password on the Home page sidebar first.")
    st.stop()

st.write(
    "Demonstrate MySQL constraint enforcement (Primary Key uniqueness, Foreign Key restrictions, and CHECK constraints) using interactive INSERT, UPDATE, and DELETE operations."
)

target_table = st.selectbox(
    "Select Table to Manage:", ["department", "insurance_provider"]
)

if target_table == "department":
    st.header("Department Management")

    # Current Records
    df_dept = run_query("SELECT * FROM department ORDER BY department_id")
    st.subheader(f"Current Departments ({len(df_dept)} rows)")
    st.dataframe(df_dept, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)

    # 1. INSERT FORM
    with col1:
        st.subheader("Add Department (INSERT)")
        with st.form("insert_dept_form"):
            new_id = st.number_input("Department ID", min_value=1, step=1, value=99)
            new_name = st.text_input("Department Name", value="Cardiology Research")
            new_type = st.selectbox("Department Type", ["Clinical", "Diagnostic", "Administrative", "Support"])
            new_floor = st.number_input("Floor Number", min_value=-5, max_value=50, value=1, help="Try a negative floor to test CHECK constraint!")
            new_status = st.selectbox("Status", ["Active", "Inactive"])

            submit_insert = st.form_submit_button("Insert Record")
            if submit_insert:
                sql = "INSERT INTO department (department_id, department_name, department_type, floor_number, status) VALUES (%s, %s, %s, %s, %s)"
                success, msg = run_execute(sql, (new_id, new_name, new_type, new_floor, new_status))
                if success:
                    st.success(f"Inserted successfully! Rows affected: {msg}")
                    st.rerun()
                else:
                    st.error(f"Operation Failed (Constraint Working):\n{msg}")

    # 2. UPDATE FORM
    with col2:
        st.subheader("Update Department (UPDATE)")
        with st.form("update_dept_form"):
            dept_ids = df_dept["department_id"].tolist() if not df_dept.empty else [1]
            upd_id = st.selectbox("Select Department ID to Update", dept_ids)
            upd_name = st.text_input("New Name", value="Updated Department")
            upd_type = st.selectbox("New Type", ["Clinical", "Diagnostic", "Administrative", "Support"], key="upd_type")
            upd_floor = st.number_input("New Floor Number", min_value=-5, max_value=50, value=2, key="upd_floor")
            upd_status = st.selectbox("New Status", ["Active", "Inactive"], key="upd_status")

            submit_update = st.form_submit_button("Update Record")
            if submit_update:
                sql = "UPDATE department SET department_name=%s, department_type=%s, floor_number=%s, status=%s WHERE department_id=%s"
                success, msg = run_execute(sql, (upd_name, upd_type, upd_floor, upd_status, upd_id))
                if success:
                    st.success(f"Updated successfully! Rows affected: {msg}")
                    st.rerun()
                else:
                    st.error(f"Operation Failed (Constraint Working):\n{msg}")

    # 3. DELETE FORM
    with col3:
        st.subheader("Delete Department (DELETE)")
        with st.form("delete_dept_form"):
            dept_ids = df_dept["department_id"].tolist() if not df_dept.empty else [1]
            del_id = st.selectbox("Select Department ID to Delete", dept_ids)
            st.caption("Note: Attempting to delete a department referenced by employees or wards will trigger Foreign Key RESTRICT rejection.")

            submit_delete = st.form_submit_button("Delete Record")
            if submit_delete:
                sql = "DELETE FROM department WHERE department_id = %s"
                success, msg = run_execute(sql, (del_id,))
                if success:
                    st.success(f"Deleted successfully! Rows affected: {msg}")
                    st.rerun()
                else:
                    st.error(f"Operation Failed (Foreign Key Restriction Working):\n{msg}")

elif target_table == "insurance_provider":
    st.header("Insurance Provider Management")

    # Current Records
    df_provider = run_query("SELECT * FROM insurance_provider ORDER BY insurance_provider_id")
    st.subheader(f"Current Insurance Providers ({len(df_provider)} rows)")
    st.dataframe(df_provider, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)

    # 1. INSERT FORM
    with col1:
        st.subheader("Add Provider (INSERT)")
        with st.form("insert_provider_form"):
            new_id = st.number_input("Provider ID", min_value=1, step=1, value=99)
            new_name = st.text_input("Provider Name", value="Global Health Care")
            new_type = st.selectbox("Provider Type", ["Private", "Government", "Corporate"])
            new_contact = st.text_input("Contact Number", value="555-9876")
            new_limit = st.number_input("Coverage Limit ($)", min_value=-50000.0, max_value=10000000.0, value=100000.0, step=5000.0, help="Try negative coverage limit to test CHECK constraint!")

            submit_insert = st.form_submit_button("Insert Record")
            if submit_insert:
                sql = "INSERT INTO insurance_provider (insurance_provider_id, provider_name, provider_type, contact_details, coverage_limit) VALUES (%s, %s, %s, %s, %s)"
                success, msg = run_execute(sql, (new_id, new_name, new_type, new_contact, new_limit))
                if success:
                    st.success(f"Inserted successfully! Rows affected: {msg}")
                    st.rerun()
                else:
                    st.error(f"Operation Failed (Constraint Working):\n{msg}")

    # 2. UPDATE FORM
    with col2:
        st.subheader("Update Provider (UPDATE)")
        with st.form("update_provider_form"):
            provider_ids = df_provider["insurance_provider_id"].tolist() if not df_provider.empty else [1]
            upd_id = st.selectbox("Select Provider ID to Update", provider_ids)
            upd_name = st.text_input("New Name", value="Updated Health Provider")
            upd_type = st.selectbox("New Type", ["Private", "Government", "Corporate"], key="upd_p_type")
            upd_contact = st.text_input("New Contact", value="555-0000", key="upd_p_contact")
            upd_limit = st.number_input("New Coverage Limit ($)", min_value=-50000.0, max_value=10000000.0, value=250000.0, key="upd_p_limit")

            submit_update = st.form_submit_button("Update Record")
            if submit_update:
                sql = "UPDATE insurance_provider SET provider_name=%s, provider_type=%s, contact_details=%s, coverage_limit=%s WHERE insurance_provider_id=%s"
                success, msg = run_execute(sql, (upd_name, upd_type, upd_contact, upd_limit, upd_id))
                if success:
                    st.success(f"Updated successfully! Rows affected: {msg}")
                    st.rerun()
                else:
                    st.error(f"Operation Failed (Constraint Working):\n{msg}")

    # 3. DELETE FORM
    with col3:
        st.subheader("Delete Provider (DELETE)")
        with st.form("delete_provider_form"):
            provider_ids = df_provider["insurance_provider_id"].tolist() if not df_provider.empty else [1]
            del_id = st.selectbox("Select Provider ID to Delete", provider_ids)
            st.caption("Note: Attempting to delete a provider referenced by patient policies will trigger Foreign Key RESTRICT rejection.")

            submit_delete = st.form_submit_button("Delete Record")
            if submit_delete:
                sql = "DELETE FROM insurance_provider WHERE insurance_provider_id = %s"
                success, msg = run_execute(sql, (del_id,))
                if success:
                    st.success(f"Deleted successfully! Rows affected: {msg}")
                    st.rerun()
                else:
                    st.error(f"Operation Failed (Foreign Key Restriction Working):\n{msg}")
