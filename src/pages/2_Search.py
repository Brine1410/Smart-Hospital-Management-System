import pandas as pd
import streamlit as st
from db import run_query

st.set_page_config(page_title="Patient Search", page_icon="🔍", layout="wide")

st.title("🔍 Patient Search & Record History")

# Password check
if not st.session_state.get("db_password"):
    st.warning("Please enter your MySQL root password on the Home page sidebar first.")
    st.stop()

st.write(
    "Search patient records by Patient ID, City, or Contact Number. Select a patient to view linked admissions, prescriptions, diagnostics, insurance, and billing histories."
)

search_term = st.text_input(
    "Enter Patient ID, City, or Contact Number:",
    placeholder="e.g. 101 or Chicago or 555-0192",
)

selected_patient_id = None

if search_term.strip():
    search_val = search_term.strip()

    # If numeric, search exact ID first or LIKE ID/city/contact
    if search_val.isdigit():
        sql_search = """
            SELECT patient_id, gender, date_of_birth, blood_group, city, contact_number 
            FROM patient 
            WHERE patient_id = %s OR contact_number LIKE %s
            LIMIT 50
        """
        patients_df = run_query(sql_search, (int(search_val), f"%{search_val}%"))
    else:
        sql_search = """
            SELECT patient_id, gender, date_of_birth, blood_group, city, contact_number 
            FROM patient 
            WHERE city LIKE %s OR contact_number LIKE %s
            LIMIT 50
        """
        patients_df = run_query(sql_search, (f"%{search_val}%", f"%{search_val}%"))

    if patients_df.empty:
        st.info("No matching patient records found.")
    else:
        st.subheader(f"Matching Patients ({len(patients_df)})")
        st.dataframe(patients_df, use_container_width=True, hide_index=True)

        patient_options = [
            f"ID: {row['patient_id']} | Gender: {row['gender']} | City: {row['city']} | Contact: {row['contact_number']}"
            for _, row in patients_df.iterrows()
        ]
        chosen = st.selectbox("Select Patient to View Detailed Records:", patient_options)
        if chosen:
            selected_patient_id = int(chosen.split(" | ")[0].replace("ID: ", ""))

if selected_patient_id is not None:
    st.write("---")
    st.header(f"Patient Profile & History — ID: {selected_patient_id}")

    # 1. Patient Info
    patient_info = run_query(
        "SELECT * FROM patient WHERE patient_id = %s", (selected_patient_id,)
    )
    if not patient_info.empty:
        st.subheader("Demographics")
        st.dataframe(patient_info, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        # 2. Admissions
        st.subheader("Admissions Record")
        admissions_sql = """
            SELECT 
                a.admission_id,
                a.admission_date,
                a.discharge_date,
                a.admission_type,
                a.admission_status,
                d.disease_name,
                dept.department_name,
                w.ward_name,
                b.bed_number
            FROM admission a
            LEFT JOIN disease d ON a.disease_id = d.disease_id
            LEFT JOIN department dept ON a.department_id = dept.department_id
            LEFT JOIN ward w ON a.ward_id = w.ward_id
            LEFT JOIN bed b ON a.bed_id = b.bed_id
            WHERE a.patient_id = %s
            ORDER BY a.admission_date DESC;
        """
        admissions_df = run_query(admissions_sql, (selected_patient_id,))
        if admissions_df.empty:
            st.write("No admission history found.")
        else:
            st.dataframe(admissions_df, use_container_width=True, hide_index=True)

        # 3. Prescriptions
        st.subheader("Prescriptions")
        prescriptions_sql = """
            SELECT 
                pr.prescription_id,
                pr.admission_id,
                d.drug_name,
                d.brand_name,
                d.drug_category,
                pr.dosage,
                pr.frequency,
                pr.duration_days
            FROM prescription pr
            JOIN admission a ON pr.admission_id = a.admission_id
            JOIN drug d ON pr.drug_id = d.drug_id
            WHERE a.patient_id = %s
            ORDER BY pr.prescription_id DESC;
        """
        prescriptions_df = run_query(prescriptions_sql, (selected_patient_id,))
        if prescriptions_df.empty:
            st.write("No prescription history found.")
        else:
            st.dataframe(prescriptions_df, use_container_width=True, hide_index=True)

    with col2:
        # 4. Diagnostic Tests
        st.subheader("Diagnostic Tests")
        diagnostics_sql = """
            SELECT 
                pd.patient_diagnostic_id,
                pd.admission_id,
                pd.test_date,
                dt.test_name,
                dt.test_category,
                pd.result_status,
                emp.employee_name AS doctor_name
            FROM patient_diagnostic pd
            JOIN admission a ON pd.admission_id = a.admission_id
            JOIN diagnostic_test dt ON pd.test_id = dt.test_id
            JOIN doctor doc ON pd.doctor_id = doc.doctor_id
            JOIN employee emp ON doc.employee_id = emp.employee_id
            WHERE a.patient_id = %s
            ORDER BY pd.test_date DESC;
        """
        diagnostics_df = run_query(diagnostics_sql, (selected_patient_id,))
        if diagnostics_df.empty:
            st.write("No diagnostic test history found.")
        else:
            st.dataframe(diagnostics_df, use_container_width=True, hide_index=True)

        # 5. Insurance Policies
        st.subheader("Insurance Policies")
        insurance_sql = """
            SELECT 
                pi.patient_insurance_id,
                pi.policy_number,
                ip.provider_name,
                ip.provider_type,
                pi.coverage_percentage,
                pi.policy_start_date,
                pi.policy_end_date,
                ip.coverage_limit
            FROM patient_insurance pi
            JOIN insurance_provider ip ON pi.insurance_provider_id = ip.insurance_provider_id
            WHERE pi.patient_id = %s;
        """
        insurance_df = run_query(insurance_sql, (selected_patient_id,))
        if insurance_df.empty:
            st.write("No insurance records found.")
        else:
            st.dataframe(insurance_df, use_container_width=True, hide_index=True)

    # 6. Billing History (Full Width)
    st.subheader("Billing History")
    billing_sql = """
        SELECT 
            b.bill_id,
            b.admission_id,
            b.bill_date,
            b.total_amount,
            b.insurance_covered_amount,
            b.patient_payable_amount,
            b.payment_status,
            b.payment_mode
        FROM billing b
        JOIN admission a ON b.admission_id = a.admission_id
        WHERE a.patient_id = %s
        ORDER BY b.bill_date DESC;
    """
    billing_df = run_query(billing_sql, (selected_patient_id,))
    if billing_df.empty:
        st.write("No billing history found.")
    else:
        st.dataframe(billing_df, use_container_width=True, hide_index=True)
